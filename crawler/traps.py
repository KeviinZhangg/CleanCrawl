"""Crawler trap detection: pagination, archives, filters, deep paths."""

from __future__ import annotations

import re
from urllib.parse import parse_qs, urlparse

import config
from models import TrapDecision

FILTER_PARAMS = {"sort", "order", "filter", "facet", "orderby", "sortby"}


def check_trap(url: str) -> TrapDecision:
    """Return crawl_decision='skip' with reason for trap URLs."""
    parsed = urlparse(url)
    path = parsed.path
    query = parsed.query
    qs = parse_qs(query)

    # Pagination depth
    page_match = re.search(r"/page/(\d+)", path, re.I)
    if page_match and int(page_match.group(1)) > config.MAX_PAGINATION:
        return TrapDecision(
            url=url,
            crawl_decision="skip",
            reason="pagination_depth_too_high",
        )

    if "page" in qs:
        try:
            if int(qs["page"][0]) > config.MAX_PAGINATION:
                return TrapDecision(
                    url=url,
                    crawl_decision="skip",
                    reason="pagination_depth_too_high",
                )
        except (ValueError, IndexError):
            pass

    # Calendar/archive traps
    if re.search(r"/archive/\d{4}/\d{2}", path, re.I):
        if page_match and int(page_match.group(1)) > 1:
            return TrapDecision(
                url=url,
                crawl_decision="skip",
                reason="calendar_archive_trap",
            )
        if re.search(r"/page/\d{3,}", path):
            return TrapDecision(
                url=url,
                crawl_decision="skip",
                reason="pagination_depth_too_high",
            )

    # Comment pagination
    if re.search(r"/comment-page-(\d+)", path, re.I):
        return TrapDecision(
            url=url,
            crawl_decision="skip",
            reason="comment_pagination_trap",
        )

    # Filter/sort URLs
    for param in FILTER_PARAMS:
        if param in {k.lower() for k in qs}:
            return TrapDecision(
                url=url,
                crawl_decision="skip",
                reason="filter_url_trap",
            )

    if len(qs) > config.MAX_QUERY_PARAMS:
        return TrapDecision(
            url=url,
            crawl_decision="skip",
            reason="filter_url_trap",
        )

    # Path depth
    depth = len([p for p in path.split("/") if p])
    if depth > config.MAX_PATH_DEPTH:
        return TrapDecision(
            url=url,
            crawl_decision="skip",
            reason="path_too_deep",
        )

    return TrapDecision(url=url, crawl_decision="crawl", reason=None)


def is_crawler_trap(url: str) -> tuple[bool, str | None]:
    """Legacy-compatible wrapper."""
    decision = check_trap(url)
    if decision.crawl_decision == "skip":
        return True, decision.reason
    return False, None
