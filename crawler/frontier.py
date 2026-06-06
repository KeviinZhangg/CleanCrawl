"""URL frontier: priority queue with dedup, depth, and per-domain budget."""

from __future__ import annotations

import heapq
import logging
from dataclasses import dataclass, field
from datetime import datetime

import config
from storage.db import Database

log = logging.getLogger("cleancrawl.frontier")


@dataclass(order=True)
class FrontierItem:
    priority: int
    url: str = field(compare=False)
    depth: int = field(compare=False, default=0)
    domain: str = field(compare=False, default="")


class Frontier:
    """Priority queue backed by SQLite for persistence."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self._heap: list[FrontierItem] = []
        self._seen: set[str] = set()
        self._domain_counts: dict[str, int] = {}
        self._load_state()

    def _load_state(self) -> None:
        for url, depth, status in self.db.get_frontier_urls():
            self._seen.add(url)
            if status == "queued":
                domain = url.split("/")[2] if "/" in url[8:] else ""
                heapq.heappush(
                    self._heap,
                    FrontierItem(priority=-depth, url=url, depth=depth, domain=domain),
                )
        self._domain_counts = self.db.get_domain_counts()

    def enqueue(self, url: str, depth: int = 0) -> bool:
        """Dedup by raw URL, budget-check, then enqueue. Traps checked at crawl time."""
        if url in self._seen:
            return False

        domain = url.split("/")[2] if "://" in url else ""
        count = self._domain_counts.get(domain, 0)
        if count >= config.PER_DOMAIN_BUDGET:
            self.db.add_frontier(url, depth, "skipped", "domain_budget_exceeded")
            self._seen.add(url)
            return False

        self._seen.add(url)
        self.db.add_frontier(url, depth, "queued")
        heapq.heappush(
            self._heap,
            FrontierItem(priority=-depth, url=url, depth=depth, domain=domain),
        )
        return True

    def dequeue(self) -> FrontierItem | None:
        while self._heap:
            item = heapq.heappop(self._heap)
            self.db.update_frontier_status(item.url, "in_progress")
            return item
        return None

    def mark_done(self, url: str, domain: str) -> None:
        self.db.update_frontier_status(url, "done")
        self._domain_counts[domain] = self._domain_counts.get(domain, 0) + 1

    def mark_blocked(self, url: str) -> None:
        self.db.update_frontier_status(url, "blocked")

    def mark_skipped(self, url: str, reason: str) -> None:
        self.db.update_frontier_status(url, "skipped", reason)

    def empty(self) -> bool:
        return len(self._heap) == 0

    def seed(self, urls: list[str]) -> int:
        added = 0
        for url in urls:
            if self.enqueue(url, depth=0):
                added += 1
        return added
