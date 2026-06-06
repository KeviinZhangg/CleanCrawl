"""Canonical data shapes matching the hackathon spec."""

from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class FetchResult:
    url: str
    status: int | str = "ok"
    html: Optional[str] = None
    blocked: bool = False
    blocked_reason: Optional[str] = None
    should_retry: bool = False
    elapsed_ms: float = 0.0
    suspicious_thin_content: bool = False

    def as_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d.pop("html", None)
        if self.blocked:
            d["status"] = "blocked"
        return d


@dataclass
class PageClassification:
    url: str
    page_type: str = "other"
    is_content_page: bool = False
    confidence: float = 0.0
    skip_reason: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "page_type": self.page_type,
            "is_content_page": self.is_content_page,
            "confidence": self.confidence,
        }


@dataclass
class ArticleContent:
    url: str
    canonical_url: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    language: Optional[str] = None
    main_content: Optional[str] = None
    summary: Optional[str] = None
    headings: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    source_domain: Optional[str] = None
    page_type: Optional[str] = None
    quality_score: float = 0.0
    quality_factors: dict[str, float] = field(default_factory=dict)
    quality_reasons: list[str] = field(default_factory=list)
    html_quality: str = "ok"
    problems_detected: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DuplicateResult:
    is_duplicate: bool = False
    duplicate_of: Optional[str] = None
    duplicate_reason: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TrapDecision:
    url: str
    crawl_decision: str = "crawl"
    reason: Optional[str] = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "crawl_decision": self.crawl_decision,
            "reason": self.reason,
        }
