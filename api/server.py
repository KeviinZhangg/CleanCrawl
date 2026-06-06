"""FastAPI HTTP API for CleanCrawl dashboard."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles

from config import settings
from api.jobs import create_job, get_job, job_to_model
from api.runner import run_job
from api.schemas import Article, CrawlJob, CrawlLogEntry, CrawlStats, StartCrawlRequest
from stats.api_stats import to_api_stats
from storage.db import Database

app = FastAPI(title="CleanCrawl API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _row_to_article(row: dict) -> Article:
    headings = row.get("headings") or "[]"
    images = row.get("images") or "[]"
    factors = row.get("quality_factors") or "{}"
    reasons = row.get("quality_reasons") or "[]"
    problems = row.get("problems_detected") or "[]"
    if isinstance(headings, str):
        headings = json.loads(headings)
    if isinstance(images, str):
        images = json.loads(images)
    if isinstance(factors, str):
        factors = json.loads(factors)
    if isinstance(reasons, str):
        reasons = json.loads(reasons)
    if isinstance(problems, str):
        problems = json.loads(problems)
    return Article(
        id=row["id"],
        url=row["url"],
        canonical_url=row.get("canonical_url"),
        title=row.get("title"),
        author=row.get("author"),
        published_date=row.get("published_date"),
        page_type=row.get("page_type"),
        language=row.get("language"),
        summary=row.get("summary"),
        main_content=row.get("main_content"),
        headings=headings,
        images=images,
        source_domain=row.get("source_domain"),
        quality_score=row.get("quality_score") or 0.0,
        quality_factors=factors,
        quality_reasons=reasons,
        html_quality=row.get("html_quality") or "ok",
        problems_detected=problems,
        is_duplicate=False,
        duplicate_of=None,
    )


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/crawls", response_model=CrawlJob)
async def start_crawl(body: StartCrawlRequest) -> CrawlJob:
    seeds = [s.strip() for s in body.seeds if s.strip() and not s.startswith("#")]
    if not seeds:
        raise HTTPException(400, "At least one seed URL required")
    if len(seeds) > settings.MAX_CRAWL_SEEDS:
        raise HTTPException(
            400,
            f"Too many seeds ({len(seeds)}). Max {settings.MAX_CRAWL_SEEDS} per crawl.",
        )
    options = body.options.model_dump()
    if options.get("render") and not settings.ENABLE_BROWSER:
        options["render"] = False
    job = create_job(seeds, options)
    job.task = asyncio.create_task(run_job(job))
    db = Database()
    try:
        return job_to_model(job, db)
    finally:
        db.close()


@app.get("/api/crawls/{job_id}", response_model=CrawlJob)
async def get_crawl(job_id: str) -> CrawlJob:
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Crawl job not found")
    db = Database()
    try:
        return job_to_model(job, db)
    finally:
        db.close()


@app.get("/api/crawls/{job_id}/events")
async def crawl_events(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Crawl job not found")

    async def event_generator():
        while True:
            item = await job.event_queue.get()
            if item is None:
                yield "event: close\ndata: {}\n\n"
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.get("/api/crawls/{job_id}/log", response_model=list[CrawlLogEntry])
async def crawl_log(job_id: str) -> list[CrawlLogEntry]:
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Crawl job not found")
    db = Database()
    try:
        from api.runner import _row_to_log_entry

        rows = db.get_crawl_logs_since(job.log_offset)
        return [_row_to_log_entry(r) for r in rows]
    finally:
        db.close()


@app.get("/api/stats", response_model=CrawlStats)
async def global_stats() -> CrawlStats:
    db = Database()
    try:
        return CrawlStats(**to_api_stats(db))
    finally:
        db.close()


@app.get("/api/articles", response_model=list[Article])
async def list_articles(
    q: str | None = None,
    page_type: str | None = None,
    min_quality: float | None = None,
    sort: str = Query("quality", pattern="^(quality|date)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[Article]:
    db = Database()
    try:
        rows = db.query_articles(
            q=q, page_type=page_type, min_quality=min_quality, sort=sort, limit=limit, offset=offset
        )
        return [_row_to_article(r) for r in rows]
    finally:
        db.close()


@app.get("/api/articles/{article_id}", response_model=Article)
async def get_article(article_id: int) -> Article:
    db = Database()
    try:
        row = db.get_article(article_id)
        if not row:
            raise HTTPException(404, "Article not found")
        return _row_to_article(row)
    finally:
        db.close()


_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(_frontend_dist), html=True), name="frontend")
