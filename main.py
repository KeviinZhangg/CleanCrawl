"""
CleanCrawl — GNOMI Hackathon 2026
CLI entry point: crawl, stats, demo
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urljoin

import config
from crawler.browser import render_page
from crawler.classifier import classify_page
from crawler.deduplicator import Deduplicator
from crawler.extractor import extract_content
from crawler.fetcher import Fetcher
from crawler.frontier import Frontier
from crawler.quality import apply_quality
from crawler.traps import check_trap
from models import FetchResult
from scheduler.recrawl import RecrawlScheduler
from stats.report import print_stats
from storage.db import Database

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("cleancrawl")

FIXTURES_DIR = Path(__file__).parent / "fixtures"

# why: demo duplicate variants all map to one fixture so dedup is testable offline
DUPLICATE_URL_MAP = {
    "https://example.com/article/ai-news": ("ai_news", "https://example.com/article/ai-news"),
    "https://example.com/article/ai-news?utm_source=twitter": ("ai_news", "https://example.com/article/ai-news?utm_source=twitter"),
    "https://example.com/amp/article/ai-news": ("ai_news", "https://example.com/amp/article/ai-news"),
    "https://example.com/mobile/article/ai-news": ("ai_news", "https://example.com/mobile/article/ai-news"),
    "https://example.com/print/article/ai-news": ("ai_news", "https://example.com/print/article/ai-news"),
}


class Pipeline:
    """Orchestrates the full crawl path for a single URL."""

    def __init__(
        self,
        db: Database,
        fetcher: Fetcher,
        dedup: Deduplicator,
        use_browser: bool = False,
        max_depth: int = 0,
    ) -> None:
        self.db = db
        self.fetcher = fetcher
        self.dedup = dedup
        self.use_browser = use_browser
        self.max_depth = max_depth
        self.frontier = Frontier(db)

    async def crawl_url(self, url: str, depth: int = 0) -> bool:
        """Full pipeline: trap → fetch → classify → extract → dedup → quality → store."""
        log.info("Crawling: %s (depth=%d)", url, depth)

        # Fixture support: fixture://cloudflare → load local HTML
        if url.startswith("fixture://"):
            return await self._crawl_fixture(url, depth)

        # Demo duplicate variants (offline, no real fetch)
        if url in DUPLICATE_URL_MAP:
            fixture_name, fake_url = DUPLICATE_URL_MAP[url]
            return await self._crawl_fixture(f"fixture://{fixture_name}", depth, override_url=fake_url)

        trap = check_trap(url)
        if trap.crawl_decision == "skip":
            log.info("SKIP (trap) %s — %s", url, trap.reason)
            self.db.log_crawl(url, skip_reason=trap.reason)
            self.frontier.mark_skipped(url, trap.reason or "trap")
            return False

        fetch = await self.fetcher.fetch(url)
        if fetch.blocked:
            log.warning("BLOCKED %s — %s", url, fetch.blocked_reason)
            self.db.log_crawl(url, fetch=fetch)
            self.frontier.mark_blocked(url)
            return False

        if not fetch.html:
            self.db.log_crawl(url, fetch=fetch, skip_reason="no_html")
            return False

        html = fetch.html
        if fetch.suspicious_thin_content and self.use_browser:
            rendered = await render_page(url)
            if rendered:
                html = rendered
                log.info("Re-extracted after JS render: %s", url)

        classification = classify_page(url, html)
        if not classification.is_content_page:
            log.info("SKIP (not content) %s — %s", url, classification.skip_reason)
            self.db.log_crawl(
                url,
                fetch=fetch,
                skip_reason=classification.skip_reason or "low_confidence",
                page_type=classification.page_type,
            )
            self.frontier.mark_skipped(url, classification.skip_reason or "low_confidence")
            return False

        article = extract_content(url, html, classification)
        max_sim = self.dedup.max_similarity(article)
        dup = self.dedup.check(article)

        if dup.is_duplicate:
            log.info("DUPLICATE %s — %s", url, dup.duplicate_reason)
            self.db.log_crawl(
                url,
                fetch=fetch,
                is_duplicate=True,
                duplicate_reason=dup.duplicate_reason,
                page_type=classification.page_type,
            )
            return False

        apply_quality(article, max_sim)
        extraction_ok = bool(article.main_content and article.title)

        self.db.save_article(article)
        self.db.log_crawl(
            url,
            fetch=fetch,
            page_type=classification.page_type,
            quality_score=article.quality_score,
            html_quality=article.html_quality,
            extraction_ok=extraction_ok,
        )
        self.frontier.mark_done(url, article.source_domain or "")

        log.info(
            "SAVED '%s' quality=%.2f reasons=%s",
            article.title,
            article.quality_score,
            article.quality_reasons,
        )

        if depth < self.max_depth and article.main_content:
            self._enqueue_links(url, html, depth)

        return True

    async def _crawl_fixture(
        self, url: str, depth: int, override_url: str | None = None
    ) -> bool:
        """Process a local HTML fixture via fixture://name path."""
        name = url.replace("fixture://", "")
        fixture_path = FIXTURES_DIR / f"{name}.html"
        if not fixture_path.exists():
            log.error("Fixture not found: %s", fixture_path)
            return False

        html = fixture_path.read_text(encoding="utf-8")
        fake_url = override_url or f"https://example.com/{name}"

        trap = check_trap(fake_url)
        if trap.crawl_decision == "skip" and "archive" in name:
            self.db.log_crawl(fake_url, skip_reason=trap.reason)
            return False

        fetch = FetchResult(url=fake_url, status=200, html=html, elapsed_ms=1.0)

        if "cloudflare" in name or "captcha" in name:
            from crawler.fetcher import detect_block

            blocked, reason, should_retry = detect_block(200, {}, html)
            if blocked:
                fetch.blocked = True
                fetch.blocked_reason = reason
                fetch.should_retry = should_retry
                self.db.log_crawl(fake_url, fetch=fetch)
                return False

        classification = classify_page(fake_url, html)
        if not classification.is_content_page and "category" in name:
            self.db.log_crawl(
                fake_url,
                fetch=fetch,
                skip_reason=classification.skip_reason,
                page_type=classification.page_type,
            )
            return False

        if "category" in name or "tag" in name:
            self.db.log_crawl(
                fake_url,
                fetch=fetch,
                skip_reason=classification.skip_reason or "not_content",
            )
            return False

        article = extract_content(fake_url, html, classification)
        max_sim = self.dedup.max_similarity(article)
        dup = self.dedup.check(article)

        if dup.is_duplicate:
            self.db.log_crawl(
                fake_url,
                fetch=fetch,
                is_duplicate=True,
                duplicate_reason=dup.duplicate_reason,
            )
            return False

        apply_quality(article, max_sim)
        self.db.save_article(article)
        self.db.log_crawl(
            fake_url,
            fetch=fetch,
            page_type=classification.page_type,
            quality_score=article.quality_score,
            html_quality=article.html_quality,
            extraction_ok=bool(article.main_content),
        )
        return True

    def _enqueue_links(self, base_url: str, html: str, depth: int) -> None:
        from bs4 import BeautifulSoup
        from urllib.parse import urlparse

        soup = BeautifulSoup(html, "lxml")
        base_domain = urlparse(base_url).netloc
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("#") or href.startswith("mailto:"):
                continue
            full = urljoin(base_url, href)
            if urlparse(full).netloc == base_domain:
                self.frontier.enqueue(full, depth=depth + 1)

    async def run(self, seed_urls: list[str]) -> int:
        added = self.frontier.seed(seed_urls)
        log.info("Seeded %d URLs", added)

        saved = 0
        sem = asyncio.Semaphore(config.MAX_CONCURRENCY)

        async def worker() -> None:
            nonlocal saved
            while True:
                item = self.frontier.dequeue()
                if item is None:
                    break
                async with sem:
                    if await self.crawl_url(item.url, item.depth):
                        saved += 1

        workers = [asyncio.create_task(worker()) for _ in range(config.MAX_CONCURRENCY)]
        await asyncio.gather(*workers)
        return saved


async def run_crawl(
    seed_urls: list[str],
    database_url: str | None = None,
    use_browser: bool = False,
    max_depth: int = 0,
) -> int:
    db = Database(database_url)
    fetcher = Fetcher()
    dedup = Deduplicator()
    dedup.load_from_db(db.get_dedup_index_rows())

    pipeline = Pipeline(db, fetcher, dedup, use_browser=use_browser, max_depth=max_depth)
    try:
        saved = await pipeline.run(seed_urls)
        log.info("Done — %d articles saved", saved)
        return saved
    finally:
        await fetcher.close()
        db.close()


def load_seeds(path: str) -> list[str]:
    with open(path) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def cmd_crawl(args: argparse.Namespace) -> None:
    seeds = load_seeds(args.seeds_file)
    asyncio.run(
        run_crawl(
            seeds,
            database_url=config.database_url_from_cli(args.db),
            use_browser=args.render,
            max_depth=args.max_depth,
        )
    )


def cmd_stats(args: argparse.Namespace) -> None:
    db = Database(config.database_url_from_cli(args.db))
    print_stats(db)
    db.close()


def cmd_demo(args: argparse.Namespace) -> None:
    demo_seeds = Path(__file__).parent / "demo_seeds.txt"
    if not demo_seeds.exists():
        log.error("demo_seeds.txt not found")
        sys.exit(1)
    seeds = load_seeds(str(demo_seeds))
    asyncio.run(
        run_crawl(
            seeds,
            database_url=config.database_url_from_cli(args.db),
            use_browser=args.render,
            max_depth=0,
        )
    )
    db = Database(config.database_url_from_cli(args.db))
    print_stats(db)
    db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="CleanCrawl — respectful article crawler")
    parser.add_argument("--db", default=config.DB_PATH, help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    crawl_p = sub.add_parser("crawl", help="Crawl seed URLs from a file")
    crawl_p.add_argument("seeds_file", help="Path to seed URLs (one per line)")
    crawl_p.add_argument("--render", action="store_true", help="Enable JS rendering fallback")
    crawl_p.add_argument("--max-depth", type=int, default=0, help="Max link-following depth")
    crawl_p.set_defaults(func=cmd_crawl)

    stats_p = sub.add_parser("stats", help="Show crawl statistics")
    stats_p.set_defaults(func=cmd_stats)

    demo_p = sub.add_parser("demo", help="Run demo seed set + show stats")
    demo_p.add_argument("--render", action="store_true", help="Enable JS rendering fallback")
    demo_p.set_defaults(func=cmd_demo)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
