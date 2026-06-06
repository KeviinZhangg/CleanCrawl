"""Pydantic models matching the frontend API contract (§3)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

CrawlStatus = Literal["queued", "running", "done", "error"]
LogDecision = Literal["saved", "blocked", "duplicate", "skipped", "error"]


class CrawlOptions(BaseModel):
    render: bool = False
    max_depth: int = 0


class StartCrawlRequest(BaseModel):
    seeds: list[str]
    options: CrawlOptions = Field(default_factory=CrawlOptions)


class CrawlStats(BaseModel):
    attempted: int = 0
    saved: int = 0
    blocked: int = 0
    duplicates: int = 0
    traps_skipped: int = 0
    success_rate: float = 0.0
    extraction_success_rate: float = 0.0
    avg_quality: float = 0.0
    blocked_by_reason: dict[str, int] = Field(default_factory=dict)
    by_domain: dict[str, dict[str, int]] = Field(default_factory=dict)


class CrawlJob(BaseModel):
    id: str
    seeds: list[str]
    status: CrawlStatus
    started_at: str
    finished_at: str | None = None
    stats: CrawlStats = Field(default_factory=CrawlStats)


class CrawlLogEntry(BaseModel):
    url: str
    decision: LogDecision
    status: int = 0
    blocked_reason: str | None = None
    skip_reason: str | None = None
    duplicate_reason: str | None = None
    quality_score: float | None = None
    timestamp: str


class Article(BaseModel):
    id: int
    url: str
    canonical_url: str | None = None
    title: str | None = None
    author: str | None = None
    published_date: str | None = None
    page_type: str | None = None
    language: str | None = None
    summary: str | None = None
    main_content: str | None = None
    headings: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    source_domain: str | None = None
    quality_score: float = 0.0
    quality_factors: dict[str, float] = Field(default_factory=dict)
    quality_reasons: list[str] = Field(default_factory=list)
    html_quality: str = "ok"
    problems_detected: list[str] = Field(default_factory=list)
    is_duplicate: bool = False
    duplicate_of: str | None = None
