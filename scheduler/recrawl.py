"""Adaptive recrawl scheduler with TTL based on page type and content changes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import config
from storage.db import Database


class RecrawlScheduler:
    """Adjust recrawl intervals based on whether content changed."""

    MIN_TTL_HOURS = 6
    MAX_TTL_HOURS = 720  # 30 days

    def __init__(self, db: Database) -> None:
        self.db = db

    def base_ttl(self, page_type: str) -> int:
        return config.RECrawl_TTL.get(page_type, config.RECrawl_TTL["other"])

    def compute_next_recrawl(
        self,
        page_type: str,
        content_changed: bool,
        current_ttl_hours: int | None = None,
    ) -> tuple[datetime, int, str]:
        base = current_ttl_hours or self.base_ttl(page_type)
        if content_changed:
            new_ttl = max(self.MIN_TTL_HOURS, int(base * 0.5))
            reason = "content_changed_ttl_halved"
        else:
            new_ttl = min(self.MAX_TTL_HOURS, int(base * 1.5))
            reason = "content_unchanged_ttl_extended"
        return datetime.now(timezone.utc) + timedelta(hours=new_ttl), new_ttl, reason

    def get_due_urls(self) -> list[str]:
        return self.db.get_due_recrawl_urls()

    def update_recrawl(self, url: str, page_type: str, content_changed: bool) -> None:
        current_ttl = None
        if self.db.get_next_recrawl_at(url):
            current_ttl = self.base_ttl(page_type)
        next_at, _, _ = self.compute_next_recrawl(page_type, content_changed, current_ttl)
        self.db.update_recrawl_at(url, next_at.isoformat())
