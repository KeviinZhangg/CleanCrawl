"""Database layer — SQLAlchemy Core, SQLite locally or Postgres in cloud."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    func,
    or_,
    select,
    update,
)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import Engine

from config import settings
from models import ArticleContent, FetchResult

metadata = MetaData()

articles = Table(
    "articles",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("url", String(2048), unique=True, nullable=False),
    Column("canonical_url", String(2048)),
    Column("title", Text),
    Column("author", String(512)),
    Column("published_date", String(64)),
    Column("language", String(16)),
    Column("page_type", String(64)),
    Column("main_content", Text),
    Column("summary", Text),
    Column("headings", Text),
    Column("images", Text),
    Column("quality_score", Float),
    Column("quality_factors", Text),
    Column("quality_reasons", Text),
    Column("html_quality", String(16)),
    Column("problems_detected", Text),
    Column("content_hash", String(128)),
    Column("source_domain", String(256)),
    Column("next_recrawl_at", String(64)),
    Column("crawled_at", String(64)),
)

frontier = Table(
    "frontier",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("url", String(2048), unique=True, nullable=False),
    Column("depth", Integer, default=0),
    Column("status", String(32), default="queued"),
    Column("skip_reason", String(256)),
    Column("created_at", String(64)),
)

crawl_log = Table(
    "crawl_log",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("url", String(2048), nullable=False),
    Column("status", String(32)),
    Column("blocked", Boolean, default=False),
    Column("blocked_reason", String(256)),
    Column("is_duplicate", Boolean, default=False),
    Column("duplicate_reason", String(256)),
    Column("skip_reason", String(256)),
    Column("page_type", String(64)),
    Column("quality_score", Float),
    Column("html_quality", String(16)),
    Column("extraction_ok", Boolean),
    Column("elapsed_ms", Float),
    Column("crawled_at", String(64)),
)


def _row_to_dict(row) -> dict[str, Any]:
    return dict(row._mapping)


class Database:
    def __init__(self, database_url: str | None = None) -> None:
        url = database_url or settings.resolved_database_url
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        self.engine: Engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
        self.database_url = url
        metadata.create_all(self.engine)

    def _upsert(self, table: Table, values: dict, index_cols: list[str], update_cols: list[str]):
        if settings.is_sqlite:
            stmt = sqlite_insert(table).values(**values)
            stmt = stmt.on_conflict_do_update(
                index_elements=index_cols,
                set_={c: stmt.excluded[c] for c in update_cols},
            )
        else:
            stmt = pg_insert(table).values(**values)
            stmt = stmt.on_conflict_do_update(
                index_elements=index_cols,
                set_={c: stmt.excluded[c] for c in update_cols},
            )
        return stmt

    def save_article(self, article: ArticleContent) -> None:
        from crawler.deduplicator import content_hash

        chash = content_hash(article.main_content) if article.main_content else None
        now = datetime.now(timezone.utc).isoformat()
        values = {
            "url": article.url,
            "canonical_url": article.canonical_url,
            "title": article.title,
            "author": article.author,
            "published_date": article.published_date,
            "language": article.language,
            "page_type": article.page_type,
            "main_content": article.main_content,
            "summary": article.summary,
            "headings": json.dumps(article.headings),
            "images": json.dumps(article.images),
            "quality_score": article.quality_score,
            "quality_factors": json.dumps(article.quality_factors),
            "quality_reasons": json.dumps(article.quality_reasons),
            "html_quality": article.html_quality,
            "problems_detected": json.dumps(article.problems_detected),
            "content_hash": chash,
            "source_domain": article.source_domain,
            "crawled_at": now,
        }
        update_cols = [k for k in values if k != "url"]
        stmt = self._upsert(articles, values, ["url"], update_cols)
        with self.engine.begin() as conn:
            conn.execute(stmt)

    def log_crawl(
        self,
        url: str,
        fetch: FetchResult | None = None,
        *,
        is_duplicate: bool = False,
        duplicate_reason: str | None = None,
        skip_reason: str | None = None,
        page_type: str | None = None,
        quality_score: float | None = None,
        html_quality: str | None = None,
        extraction_ok: bool | None = None,
    ) -> None:
        status = "blocked" if fetch and fetch.blocked else (str(fetch.status) if fetch else "skipped")
        with self.engine.begin() as conn:
            conn.execute(
                crawl_log.insert().values(
                    url=url,
                    status=status,
                    blocked=bool(fetch.blocked) if fetch else False,
                    blocked_reason=fetch.blocked_reason if fetch else None,
                    is_duplicate=is_duplicate,
                    duplicate_reason=duplicate_reason,
                    skip_reason=skip_reason,
                    page_type=page_type,
                    quality_score=quality_score,
                    html_quality=html_quality,
                    extraction_ok=extraction_ok,
                    elapsed_ms=fetch.elapsed_ms if fetch else None,
                    crawled_at=datetime.now(timezone.utc).isoformat(),
                )
            )

    def add_frontier(
        self, url: str, depth: int, status: str, skip_reason: str | None = None
    ) -> None:
        values = {
            "url": url,
            "depth": depth,
            "status": status,
            "skip_reason": skip_reason,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if settings.is_sqlite:
            stmt = sqlite_insert(frontier).values(**values).on_conflict_do_nothing(index_elements=["url"])
        else:
            stmt = pg_insert(frontier).values(**values).on_conflict_do_nothing(index_elements=["url"])
        with self.engine.begin() as conn:
            conn.execute(stmt)

    def update_frontier_status(
        self, url: str, status: str, skip_reason: str | None = None
    ) -> None:
        vals: dict[str, Any] = {"status": status}
        if skip_reason is not None:
            vals["skip_reason"] = skip_reason
        with self.engine.begin() as conn:
            conn.execute(update(frontier).where(frontier.c.url == url).values(**vals))

    def get_frontier_urls(self) -> list[tuple[str, int, str]]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(frontier.c.url, frontier.c.depth, frontier.c.status)).fetchall()
        return [(r.url, r.depth, r.status) for r in rows]

    def get_domain_counts(self) -> dict[str, int]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                select(articles.c.source_domain, func.count().label("cnt"))
                .where(articles.c.source_domain.isnot(None))
                .group_by(articles.c.source_domain)
            ).fetchall()
        return {r.source_domain: r.cnt for r in rows}

    def get_dedup_index_rows(self) -> list[tuple]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                select(
                    articles.c.url,
                    articles.c.canonical_url,
                    articles.c.title,
                    articles.c.published_date,
                    articles.c.content_hash,
                )
            ).fetchall()
        return [(r.url, r.canonical_url, r.title, r.published_date, r.content_hash) for r in rows]

    def get_crawl_log_stats(self) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(crawl_log)).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_all_crawl_logs(self) -> list[dict[str, Any]]:
        return self.get_crawl_log_stats()

    def get_articles(self) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(select(articles)).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_article(self, article_id: int) -> dict[str, Any] | None:
        with self.engine.connect() as conn:
            row = conn.execute(select(articles).where(articles.c.id == article_id)).fetchone()
        return _row_to_dict(row) if row else None

    def query_articles(
        self,
        *,
        q: str | None = None,
        page_type: str | None = None,
        min_quality: float | None = None,
        sort: str = "quality",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        stmt = select(articles)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(
                    articles.c.title.ilike(like),
                    articles.c.main_content.ilike(like),
                    articles.c.url.ilike(like),
                )
            )
        if page_type:
            stmt = stmt.where(articles.c.page_type == page_type)
        if min_quality is not None:
            stmt = stmt.where(articles.c.quality_score >= min_quality)
        order_col = (
            articles.c.quality_score.desc()
            if sort == "quality"
            else articles.c.published_date.desc()
        )
        stmt = stmt.order_by(order_col).limit(limit).offset(offset)
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).fetchall()
        return [_row_to_dict(r) for r in rows]

    def get_crawl_logs_since(self, offset: int = 0) -> list[dict[str, Any]]:
        with self.engine.connect() as conn:
            rows = conn.execute(
                select(crawl_log).order_by(crawl_log.c.id).offset(offset)
            ).fetchall()
        return [_row_to_dict(r) for r in rows]

    def crawl_log_count(self) -> int:
        with self.engine.connect() as conn:
            return conn.execute(select(func.count()).select_from(crawl_log)).scalar() or 0

    def article_count(self) -> int:
        with self.engine.connect() as conn:
            return conn.execute(select(func.count()).select_from(articles)).scalar() or 0

    def get_due_recrawl_urls(self) -> list[str]:
        now = datetime.now(timezone.utc).isoformat()
        with self.engine.connect() as conn:
            rows = conn.execute(
                select(articles.c.url).where(
                    articles.c.next_recrawl_at.isnot(None),
                    articles.c.next_recrawl_at <= now,
                )
            ).fetchall()
        return [r.url for r in rows]

    def get_next_recrawl_at(self, url: str) -> str | None:
        with self.engine.connect() as conn:
            row = conn.execute(
                select(articles.c.next_recrawl_at).where(articles.c.url == url)
            ).fetchone()
        return row.next_recrawl_at if row else None

    def update_recrawl_at(self, url: str, next_at: str) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                update(articles).where(articles.c.url == url).values(next_recrawl_at=next_at)
            )

    def close(self) -> None:
        self.engine.dispose()
