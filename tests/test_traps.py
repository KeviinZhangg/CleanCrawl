"""Tests for crawler trap detection."""

import pytest

from crawler.traps import check_trap, is_crawler_trap


def test_pagination_trap():
    url = "https://example.com/archive/2021/05/page/400"
    decision = check_trap(url)
    assert decision.crawl_decision == "skip"
    assert decision.reason == "pagination_depth_too_high"


def test_filter_url_trap():
    url = "https://example.com/search?sort=date&order=desc&filter=tech&facet=ai&page=1"
    decision = check_trap(url)
    assert decision.crawl_decision == "skip"
    assert decision.reason in ("filter_url_trap", "pagination_depth_too_high")


def test_normal_article_allowed():
    url = "https://example.com/news/2026/ai-regulation-explained"
    decision = check_trap(url)
    assert decision.crawl_decision == "crawl"


def test_comment_pagination_trap():
    url = "https://example.com/blog/post/comment-page-3"
    decision = check_trap(url)
    assert decision.crawl_decision == "skip"
    assert decision.reason == "comment_pagination_trap"


def test_legacy_wrapper():
    is_trap, reason = is_crawler_trap("https://example.com/archive/2021/05/page/400")
    assert is_trap is True
    assert reason == "pagination_depth_too_high"
