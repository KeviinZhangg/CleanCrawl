"""All tunable thresholds and deployment settings — env vars override defaults."""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Twelve-factor config: same code, different env per environment."""

    DATABASE_URL: str = "sqlite:///cleancrawl.db"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000"
    USER_AGENT: str = "CleanCrawlBot/1.0 (+https://example.com/cleancrawlbot)"
    ENABLE_BROWSER: bool = False
    MAX_CRAWL_SEEDS: int = 30

    # Crawler tuning (overridable in cloud without code changes)
    DEFAULT_CRAWL_DELAY: float = 1.5
    MAX_CONCURRENCY: int = 8
    PER_DOMAIN_CONCURRENCY: int = 1
    REQUEST_TIMEOUT: int = 15
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_BASE: float = 1.5
    CLASSIFIER_CONTENT_THRESHOLD: float = 0.40
    MIN_ARTICLE_WORDS: int = 250
    HIGH_LINK_COUNT: int = 100
    MAX_PAGINATION: int = 20
    MAX_QUERY_PARAMS: int = 4
    MAX_PATH_DEPTH: int = 8
    PER_DOMAIN_BUDGET: int = 500
    NEAR_DUP_JACCARD: float = 0.85
    TITLE_SIM_THRESHOLD: float = 0.90
    SHINGLE_SIZE: int = 5
    MINHASH_PERM: int = 128

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_postgres(self) -> bool:
        return self.resolved_database_url.startswith("postgresql")

    @property
    def resolved_database_url(self) -> str:
        """Normalize platform URLs (Render uses postgres://)."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql+psycopg2://", 1)
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Backward-compatible module-level aliases used across the codebase
DEFAULT_CRAWL_DELAY = settings.DEFAULT_CRAWL_DELAY
MAX_CONCURRENCY = settings.MAX_CONCURRENCY
PER_DOMAIN_CONCURRENCY = settings.PER_DOMAIN_CONCURRENCY
REQUEST_TIMEOUT = settings.REQUEST_TIMEOUT
USER_AGENT = settings.USER_AGENT
MAX_RETRIES = settings.MAX_RETRIES
RETRY_BACKOFF_BASE = settings.RETRY_BACKOFF_BASE
RETRYABLE_STATUS = {500, 502, 503, 504, 429}
CLASSIFIER_CONTENT_THRESHOLD = settings.CLASSIFIER_CONTENT_THRESHOLD
MIN_ARTICLE_WORDS = settings.MIN_ARTICLE_WORDS
HIGH_LINK_COUNT = settings.HIGH_LINK_COUNT
MAX_PAGINATION = settings.MAX_PAGINATION
MAX_QUERY_PARAMS = settings.MAX_QUERY_PARAMS
MAX_PATH_DEPTH = settings.MAX_PATH_DEPTH
PER_DOMAIN_BUDGET = settings.PER_DOMAIN_BUDGET
NEAR_DUP_JACCARD = settings.NEAR_DUP_JACCARD
TITLE_SIM_THRESHOLD = settings.TITLE_SIM_THRESHOLD
SHINGLE_SIZE = settings.SHINGLE_SIZE
MINHASH_PERM = settings.MINHASH_PERM
DATABASE_URL = settings.DATABASE_URL
DB_PATH = settings.DATABASE_URL.replace("sqlite:///", "") if settings.is_sqlite else "cleancrawl.db"

QUALITY_WEIGHTS = {
    "completeness": 0.30,
    "cleanliness": 0.25,
    "usefulness": 0.20,
    "uniqueness": 0.15,
    "freshness": 0.10,
}

RECrawl_TTL = {
    "news_article": 24,
    "blog_post": 72,
    "wiki": 168,
    "educational": 168,
    "financial": 48,
    "other": 96,
}


def database_url_from_cli(path: str) -> str:
    """CLI --db cleancrawl.db → sqlite:///cleancrawl.db"""
    if path.startswith(("sqlite:", "postgresql:")):
        return path
    return f"sqlite:///{path}"
