"""Background crawl runner with SSE event emission."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone

import config
from api.jobs import JobState, emit_done, emit_log, emit_stats, classify_decision
from api.schemas import CrawlLogEntry
from main import run_crawl
from stats.api_stats import to_api_stats
from storage.db import Database

log = logging.getLogger("cleancrawl.api")


def _row_to_log_entry(row: dict) -> CrawlLogEntry:
    status_raw = row.get("status") or "0"
    try:
        status = int(status_raw)
    except (ValueError, TypeError):
        status = 0
    return CrawlLogEntry(
        url=row["url"],
        decision=classify_decision(
            blocked=bool(row.get("blocked")),
            is_duplicate=bool(row.get("is_duplicate")),
            skip_reason=row.get("skip_reason"),
            extraction_ok=bool(row.get("extraction_ok")) if row.get("extraction_ok") is not None else None,
        ),
        status=status,
        blocked_reason=row.get("blocked_reason"),
        skip_reason=row.get("skip_reason"),
        duplicate_reason=row.get("duplicate_reason"),
        quality_score=row.get("quality_score"),
        timestamp=row.get("crawled_at") or datetime.now(timezone.utc).isoformat(),
    )


async def _poll_and_emit(job: JobState, db: Database, seen_ids: set[int]) -> int:
    rows = db.get_all_crawl_logs()
    for row in rows:
        rid = row["id"]
        if rid in seen_ids:
            continue
        seen_ids.add(rid)
        entry = _row_to_log_entry(row)
        await emit_log(job, entry)
    await emit_stats(job, db)
    return len(rows)


async def run_job(job: JobState) -> None:
    db = Database()
    seen_ids: set[int] = set()
    job.status = "running"

    crawl_task = asyncio.create_task(
        run_crawl(
            job.seeds,
            use_browser=job.options.get("render", False),
            max_depth=job.options.get("max_depth", 0),
        )
    )

    try:
        while not crawl_task.done():
            await _poll_and_emit(job, db, seen_ids)
            await asyncio.sleep(0.25)

        await crawl_task
        await _poll_and_emit(job, db, seen_ids)
        job.status = "done"
        job.finished_at = datetime.now(timezone.utc).isoformat()
        await emit_done(job, db)
    except Exception as e:
        log.exception("Crawl job %s failed: %s", job.id, e)
        job.status = "error"
        job.finished_at = datetime.now(timezone.utc).isoformat()
        await job.event_queue.put({"type": "error", "data": {"message": str(e)}})
        await job.event_queue.put(None)
    finally:
        db.close()
