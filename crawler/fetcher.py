"""Respectful HTTP fetcher with robots.txt, rate limiting, retries, and anti-bot detection."""

from __future__ import annotations

import asyncio
import logging
import random
import time
from urllib.parse import urlparse

import httpx
import protego

import config
from models import FetchResult

log = logging.getLogger("cleancrawl.fetcher")

HEADERS = {
    "User-Agent": config.USER_AGENT,
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

BLOCK_STATUS = {403, 429, 503}

BLOCK_BODY_MARKERS = {
    "cloudflare": [
        "just a moment",
        "checking your browser",
        "cf-browser-verification",
        "cf-challenge",
    ],
    "captcha": [
        "g-recaptcha",
        "hcaptcha",
        "cf-turnstile",
        "captcha-checkbox",
        "verify you are human",
        "are you a robot",
    ],
    "generic_bot": [
        "access denied",
        "unusual traffic",
        "request blocked",
        "rate limited",
    ],
}


class Fetcher:
    """Async fetcher with per-domain politeness and robots.txt compliance."""

    def __init__(self) -> None:
        self._robots_cache: dict[str, protego.Protego | None] = {}
        self._last_request: dict[str, float] = {}
        self._domain_locks: dict[str, asyncio.Lock] = {}
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=config.REQUEST_TIMEOUT,
                follow_redirects=True,
                headers=HEADERS,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _domain_lock(self, domain: str) -> asyncio.Lock:
        if domain not in self._domain_locks:
            self._domain_locks[domain] = asyncio.Lock()
        return self._domain_locks[domain]

    async def _fetch_robots(self, domain: str) -> protego.Protego | None:
        if domain in self._robots_cache:
            return self._robots_cache[domain]
        try:
            client = await self._get_client()
            resp = await client.get(f"https://{domain}/robots.txt")
            if resp.status_code == 200:
                pg = protego.Protego.parse(resp.text)
                self._robots_cache[domain] = pg
                return pg
        except Exception as e:
            log.debug("robots.txt fetch failed for %s: %s", domain, e)
        self._robots_cache[domain] = None
        return None

    async def allowed(self, url: str) -> bool:
        domain = urlparse(url).netloc
        robots = await self._fetch_robots(domain)
        if robots is None:
            return True
        return robots.can_fetch(url, config.USER_AGENT)

    async def crawl_delay(self, domain: str) -> float:
        robots = await self._fetch_robots(domain)
        if robots:
            delay = robots.crawl_delay(config.USER_AGENT)
            if delay is not None:
                return float(delay)
        return config.DEFAULT_CRAWL_DELAY

    async def _rate_limit(self, domain: str) -> None:
        delay = await self.crawl_delay(domain)
        last = self._last_request.get(domain, 0.0)
        wait = delay - (time.time() - last)
        if wait > 0:
            await asyncio.sleep(wait)
        self._last_request[domain] = time.time()

    async def fetch(self, url: str) -> FetchResult:
        domain = urlparse(url).netloc

        if not await self.allowed(url):
            return FetchResult(
                url=url,
                status="blocked",
                blocked=True,
                blocked_reason="robots_txt_disallowed",
                should_retry=False,
            )

        async with self._domain_lock(domain):
            await self._rate_limit(domain)
            return await self._fetch_with_retries(url)

    async def _fetch_with_retries(self, url: str) -> FetchResult:
        client = await self._get_client()
        last_result: FetchResult | None = None

        for attempt in range(config.MAX_RETRIES + 1):
            t0 = time.time()
            try:
                resp = await client.get(url)
                elapsed = (time.time() - t0) * 1000
                html = resp.text
                headers = dict(resp.headers)

                blocked, reason, should_retry = detect_block(
                    resp.status_code, headers, html
                )
                if blocked:
                    return FetchResult(
                        url=url,
                        status=resp.status_code,
                        html=html,
                        blocked=True,
                        blocked_reason=reason,
                        should_retry=should_retry,
                        elapsed_ms=elapsed,
                    )

                thin = detect_thin_content(html)
                return FetchResult(
                    url=url,
                    status=resp.status_code,
                    html=html,
                    elapsed_ms=elapsed,
                    suspicious_thin_content=thin,
                )

            except httpx.TimeoutException:
                elapsed = (time.time() - t0) * 1000
                last_result = FetchResult(
                    url=url,
                    status=0,
                    blocked_reason="timeout",
                    should_retry=True,
                    elapsed_ms=elapsed,
                )
            except Exception as e:
                elapsed = (time.time() - t0) * 1000
                log.error("Fetch error %s: %s", url, e)
                return FetchResult(
                    url=url,
                    status=0,
                    blocked_reason=str(e),
                    should_retry=False,
                    elapsed_ms=elapsed,
                )

            if attempt < config.MAX_RETRIES and last_result and last_result.should_retry:
                backoff = config.RETRY_BACKOFF_BASE ** attempt + random.uniform(0, 0.5)
                await asyncio.sleep(backoff)
            else:
                break

        return last_result or FetchResult(url=url, status=0, blocked_reason="unknown")


def detect_block(
    status: int, headers: dict[str, str], body: str
) -> tuple[bool, str | None, bool]:
    # why: a 200 can still be a Cloudflare challenge page, so we never trust status alone
    if status in BLOCK_STATUS:
        return True, f"http_{status}", status == 429

    h = " ".join(f"{k}:{v}" for k, v in headers.items()).lower()
    if "cf-ray" in h or "cloudflare" in h:
        for marker in BLOCK_BODY_MARKERS["cloudflare"]:
            if marker in body.lower():
                return True, "cloudflare_challenge", False

    low = body.lower()
    word_count = len(low.split())
    for reason, markers in BLOCK_BODY_MARKERS.items():
        if not any(m in low for m in markers):
            continue
        # why: long articles often mention CAPTCHA in passing — only block thin challenge pages
        if reason == "captcha" and word_count > 500:
            continue
        if reason == "generic_bot" and word_count > 1000:
            continue
        return True, f"{reason}_detected", False

    return False, None, False


def detect_thin_content(html: str) -> bool:
    """Flag pages that are 200 but suspiciously empty (SPA shells, script-only)."""
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(" ", strip=True)
    word_count = len(text.split())
    scripts = len(soup.find_all("script"))
    # why: lots of script tags with near-zero visible text suggests JS-rendered content
    return word_count < 50 and scripts >= 3


async def fetch_page(url: str, fetcher: Fetcher | None = None) -> FetchResult:
    """Convenience wrapper for single-page fetch."""
    own_fetcher = fetcher is None
    f = fetcher or Fetcher()
    try:
        return await f.fetch(url)
    finally:
        if own_fetcher:
            await f.close()
