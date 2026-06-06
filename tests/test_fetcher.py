"""Tests for fetcher anti-bot detection and rate limiting."""

import asyncio
import time
from pathlib import Path

import pytest

from crawler.fetcher import Fetcher, detect_block, detect_thin_content

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_cloudflare_fixture_blocked():
    html = (FIXTURES / "cloudflare.html").read_text()
    blocked, reason, should_retry = detect_block(200, {"server": "cloudflare"}, html)
    assert blocked is True
    assert reason == "cloudflare_challenge"
    assert should_retry is False


def test_clean_article_not_blocked():
    html = (FIXTURES / "clean_article.html").read_text()
    blocked, reason, _ = detect_block(200, {}, html)
    assert blocked is False
    assert reason is None


def test_captcha_detection():
    body = "<html><body><div class='g-recaptcha'></div>Please verify you are human to continue</body></html>"
    blocked, reason, should_retry = detect_block(200, {}, body)
    assert blocked is True
    assert "captcha" in reason
    assert should_retry is False


def test_http_403_blocked():
    blocked, reason, should_retry = detect_block(403, {}, "")
    assert blocked is True
    assert reason == "http_403"
    assert should_retry is False


def test_http_429_retryable():
    blocked, reason, should_retry = detect_block(429, {}, "")
    assert blocked is True
    assert should_retry is True


def test_thin_content_detection():
    html = (FIXTURES / "js_shell.html").read_text()
    assert detect_thin_content(html) is True


def test_normal_content_not_thin():
    html = (FIXTURES / "clean_article.html").read_text()
    assert detect_thin_content(html) is False


@pytest.mark.asyncio
async def test_rate_limiting_spacing():
    fetcher = Fetcher()
    url = "https://httpbin.org/html"
    # Use a mock approach: test internal rate limit timing
    domain = "test-spacing.example"
    fetcher._last_request[domain] = 0.0

    t0 = time.time()
    await fetcher._rate_limit(domain)
    fetcher._last_request[domain] = time.time() - 0.1  # simulate recent request
    await fetcher._rate_limit(domain)
    elapsed = time.time() - t0
    # Should have waited at least some portion of DEFAULT_CRAWL_DELAY
    assert elapsed >= 0.5
    await fetcher.close()
