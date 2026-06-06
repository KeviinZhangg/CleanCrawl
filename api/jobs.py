"""In-memory crawl job manager with SSE event queues."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from api.schemas import CrawlJob, CrawlLogEntry, CrawlStats, LogDecision
from stats.api_stats import to_api_stats
from storage.db import Database


@dataclass
class JobState:
    id: str
    seeds: list[str]
    status: str = "queued"
    started_at: str = ""
    finished_at: str | None = None
    event_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    task: asyncio.Task | None = None
    log_offset: int = 0
    options: dict[str, Any] = field(default_factory=dict)


_jobs: dict[str, JobState] = {}


def create_job(seeds: list[str], options: dict[str, Any]) -> JobState:
    job_id = str(uuid.uuid4())[:8]
    job = JobState(
        id=job_id,
        seeds=seeds,
        status="queued",
        started_at=datetime.now(timezone.utc).isoformat(),
        options=options,
    )
    _jobs[job_id] = job
    return job


def get_job(job_id: str) -> JobState | None:
    return _jobs.get(job_id)


def all_jobs() -> list[JobState]:
    return list(_jobs.values())


def job_to_model(job: JobState, db: Database) -> CrawlJob:
    stats = CrawlStats(**to_api_stats(db))
    return CrawlJob(
        id=job.id,
        seeds=job.seeds,
        status=job.status,  # type: ignore[arg-type]
        started_at=job.started_at,
        finished_at=job.finished_at,
        stats=stats,
    )


def classify_decision(
    *,
    blocked: bool = False,
    is_duplicate: bool = False,
    skip_reason: str | None = None,
    extraction_ok: bool | None = None,
) -> LogDecision:
    if blocked:
        return "blocked"
    if is_duplicate:
        return "duplicate"
    if skip_reason:
        return "skipped"
    if extraction_ok:
        return "saved"
    return "error"


async def emit_log(job: JobState, entry: CrawlLogEntry) -> None:
    await job.event_queue.put({"type": "log", "data": entry.model_dump()})


async def emit_stats(job: JobState, db: Database) -> None:
    stats = to_api_stats(db)
    await job.event_queue.put({"type": "stats", "data": stats})


async def emit_done(job: JobState, db: Database) -> None:
    job_model = job_to_model(job, db)
    await job.event_queue.put({"type": "done", "data": job_model.model_dump()})
    await job.event_queue.put(None)  # sentinel to close SSE stream
