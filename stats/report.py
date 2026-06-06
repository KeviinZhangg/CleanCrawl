"""Crawl statistics dashboard powered by crawl_log + articles."""

from __future__ import annotations

from collections import Counter, defaultdict

from rich.console import Console
from rich.table import Table

from storage.db import Database


def compute_stats(db: Database) -> dict:
    logs = db.get_crawl_log_stats()
    articles = db.get_articles()

    total = len(logs)
    blocked = [l for l in logs if l.get("blocked")]
    duplicates = [l for l in logs if l.get("is_duplicate")]
    skipped = [l for l in logs if l.get("skip_reason")]
    successful = [l for l in logs if not l.get("blocked") and not l.get("is_duplicate") and not l.get("skip_reason") and l.get("extraction_ok")]

    extraction_attempts = [l for l in logs if l.get("extraction_ok") is not None]
    extraction_ok = [l for l in extraction_attempts if l.get("extraction_ok")]

    messy = [a for a in articles if a.get("html_quality") == "messy"]
    qualities = [a["quality_score"] for a in articles if a.get("quality_score")]

    blocked_reasons = Counter(l.get("blocked_reason") or "unknown" for l in blocked)
    skip_reasons = Counter(l.get("skip_reason") or "unknown" for l in skipped)
    dup_reasons = Counter(l.get("duplicate_reason") or "unknown" for l in duplicates)

    domain_stats: dict[str, dict] = defaultdict(lambda: {"attempted": 0, "saved": 0, "blocked": 0})
    for l in logs:
        domain = _domain_from_url(l["url"])
        domain_stats[domain]["attempted"] += 1
        if l.get("blocked"):
            domain_stats[domain]["blocked"] += 1
    for a in articles:
        domain = a.get("source_domain") or _domain_from_url(a["url"])
        domain_stats[domain]["saved"] += 1

    return {
        "total_attempted": total,
        "articles_saved": len(articles),
        "crawl_success_rate": len(successful) / total if total else 0.0,
        "blocked_count": len(blocked),
        "blocked_reasons": dict(blocked_reasons),
        "duplicates_removed": len(duplicates),
        "duplicate_reasons": dict(dup_reasons),
        "traps_skipped": len(skipped),
        "skip_reasons": dict(skip_reasons),
        "extraction_success_rate": len(extraction_ok) / len(extraction_attempts) if extraction_attempts else 0.0,
        "avg_quality": sum(qualities) / len(qualities) if qualities else 0.0,
        "messy_html_count": len(messy),
        "domain_breakdown": dict(domain_stats),
    }


def _domain_from_url(url: str) -> str:
    if "://" in url:
        return url.split("/")[2]
    return "fixture"


def print_stats(db: Database) -> None:
    stats = compute_stats(db)
    console = Console()

    console.print("\n[bold cyan]CleanCrawl — Crawl Statistics[/bold cyan]\n")

    summary = Table(title="Summary", show_header=True)
    summary.add_column("Metric", style="bold")
    summary.add_column("Value", justify="right")
    summary.add_row("Total URLs Attempted", str(stats["total_attempted"]))
    summary.add_row("Articles Saved", str(stats["articles_saved"]))
    summary.add_row("Crawl Success Rate", f"{stats['crawl_success_rate']:.1%}")
    summary.add_row("Extraction Success Rate", f"{stats['extraction_success_rate']:.1%}")
    summary.add_row("Blocked Pages", str(stats["blocked_count"]))
    summary.add_row("Duplicates Removed", str(stats["duplicates_removed"]))
    summary.add_row("Traps Skipped", str(stats["traps_skipped"]))
    summary.add_row("Avg Quality Score", f"{stats['avg_quality']:.2f}")
    summary.add_row("Messy HTML Pages", str(stats["messy_html_count"]))
    console.print(summary)

    if stats["blocked_reasons"]:
        blocked_table = Table(title="Blocked by Reason")
        blocked_table.add_column("Reason")
        blocked_table.add_column("Count", justify="right")
        for reason, count in sorted(stats["blocked_reasons"].items(), key=lambda x: -x[1]):
            blocked_table.add_row(reason, str(count))
        console.print(blocked_table)

    if stats["skip_reasons"]:
        skip_table = Table(title="Skipped (Traps / Classification)")
        skip_table.add_column("Reason")
        skip_table.add_column("Count", justify="right")
        for reason, count in sorted(stats["skip_reasons"].items(), key=lambda x: -x[1]):
            skip_table.add_row(reason[:60], str(count))
        console.print(skip_table)

    if stats["domain_breakdown"]:
        domain_table = Table(title="Per-Domain Breakdown")
        domain_table.add_column("Domain")
        domain_table.add_column("Attempted", justify="right")
        domain_table.add_column("Saved", justify="right")
        domain_table.add_column("Blocked", justify="right")
        for domain, d in sorted(stats["domain_breakdown"].items()):
            domain_table.add_row(
                domain[:40],
                str(d["attempted"]),
                str(d["saved"]),
                str(d["blocked"]),
            )
        console.print(domain_table)

    console.print()
