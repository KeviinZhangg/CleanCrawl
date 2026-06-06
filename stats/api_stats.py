"""Map internal stats to the API contract (§3)."""

from __future__ import annotations

from stats.report import compute_stats
from storage.db import Database


def to_api_stats(db: Database) -> dict:
    raw = compute_stats(db)
    by_domain = {
        domain: {"saved": d["saved"], "blocked": d["blocked"]}
        for domain, d in raw["domain_breakdown"].items()
    }
    return {
        "attempted": raw["total_attempted"],
        "saved": raw["articles_saved"],
        "blocked": raw["blocked_count"],
        "duplicates": raw["duplicates_removed"],
        "traps_skipped": raw["traps_skipped"],
        "success_rate": raw["crawl_success_rate"],
        "extraction_success_rate": raw["extraction_success_rate"],
        "avg_quality": raw["avg_quality"],
        "blocked_by_reason": raw["blocked_reasons"],
        "by_domain": by_domain,
    }
