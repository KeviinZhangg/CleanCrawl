"""Heuristic page classifier: article-like vs navigation/listing pages."""

from __future__ import annotations

import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup

import config
from models import PageClassification

SKIP_URL_PATTERNS = [
    (r"/tag/", "tag_page"),
    (r"/category/", "category_page"),
    (r"/search", "search_page"),
    (r"\?q=", "search_page"),
    (r"/login", "login_page"),
    (r"/author/", "author_page"),
    (r"/page/\d+", "pagination_page"),
    (r"/archive/", "archive_page"),
    (r"/feed", "feed_page"),
    (r"\.xml$", "feed_page"),
]

BOOST_URL_PATTERNS = [
    (r"/news/", "news_article"),
    (r"/blog/", "blog_post"),
    (r"/article/", "news_article"),
    (r"/post/", "blog_post"),
    (r"/story/", "news_article"),
    (r"/wiki/", "wiki"),
    (r"/docs/", "wiki"),
    (r"/\d{4}/\d{2}/", "news_article"),
]

SCHEMA_TYPE_MAP = {
    "NewsArticle": "news_article",
    "Article": "news_article",
    "BlogPosting": "blog_post",
    "ScholarlyArticle": "educational",
    "TechArticle": "educational",
}


def classify_page(url: str, html: str) -> PageClassification:
    """Classify whether a page contains useful article-like content."""
    parsed = urlparse(url)
    path = parsed.path.lower()
    query = parsed.query.lower()

    # Homepage check
    if path in ("", "/"):
        return PageClassification(
            url=url,
            page_type="other",
            is_content_page=False,
            confidence=0.95,
            skip_reason="homepage",
        )

    # URL-based hard skips
    full = path + ("?" + query if query else "")
    for pattern, reason in SKIP_URL_PATTERNS:
        if re.search(pattern, full, re.I):
            return PageClassification(
                url=url,
                page_type="other",
                is_content_page=False,
                confidence=0.92,
                skip_reason=f"url_pattern:{reason}",
            )

    if "?q=" in full or "search?" in full:
        return PageClassification(
            url=url,
            page_type="other",
            is_content_page=False,
            confidence=0.90,
            skip_reason="url_pattern:search_page",
        )

    soup = BeautifulSoup(html, "lxml")
    score = 0.0
    page_type = "other"

    # URL boosts
    for pattern, ptype in BOOST_URL_PATTERNS:
        if re.search(pattern, path, re.I):
            score += 0.25
            page_type = ptype
            break

    # HTML structure signals
    if soup.find("article"):
        score += 0.20
        if page_type == "other":
            page_type = "news_article"

    if soup.find("main"):
        score += 0.10

    og_type = soup.find("meta", property="og:type")
    if og_type and "article" in (og_type.get("content") or "").lower():
        score += 0.20
        page_type = "news_article"

    schema = soup.find(attrs={"itemtype": re.compile(r"schema\.org/", re.I)})
    if schema:
        itemtype = schema.get("itemtype", "")
        for key, mapped in SCHEMA_TYPE_MAP.items():
            if key in itemtype:
                score += 0.25
                page_type = mapped
                break

    # JSON-LD schema
    for script in soup.find_all("script", type="application/ld+json"):
        text = script.string or ""
        for key, mapped in SCHEMA_TYPE_MAP.items():
            if key in text:
                score += 0.20
                if page_type == "other":
                    page_type = mapped

    text = soup.get_text(" ", strip=True)
    word_count = len(text.split())
    if word_count >= config.MIN_ARTICLE_WORDS:
        score += 0.15
    elif word_count < 100:
        score -= 0.25

    links = soup.find_all("a")
    link_count = len(links)
    if link_count > 0:
        text_len = max(len(text), 1)
        link_text_len = sum(len(a.get_text(strip=True)) for a in links)
        ratio = text_len / max(link_text_len, 1)
        if ratio > 3:
            score += 0.10
    if link_count > config.HIGH_LINK_COUNT:
        score -= 0.20

    # Byline / date signals
    if _has_byline(soup):
        score += 0.10
    if _has_publish_date(soup):
        score += 0.10

    # Educational / long-form heuristics
    if page_type == "other" and word_count > 800:
        headings = soup.find_all(["h1", "h2", "h3"])
        if len(headings) >= 3:
            page_type = "educational"
            score += 0.10

    confidence = round(min(max(score, 0.0), 1.0), 2)
    is_content = score >= config.CLASSIFIER_CONTENT_THRESHOLD

    return PageClassification(
        url=url,
        page_type=page_type,
        is_content_page=is_content,
        confidence=confidence,
        skip_reason=None if is_content else "low_confidence",
    )


def _has_byline(soup: BeautifulSoup) -> bool:
    selectors = [
        {"class_": re.compile(r"author|byline|writer", re.I)},
        {"rel": "author"},
        {"itemprop": "author"},
    ]
    for sel in selectors:
        if soup.find(attrs=sel):
            return True
    return False


def _has_publish_date(soup: BeautifulSoup) -> bool:
    if soup.find("time"):
        return True
    if soup.find(attrs={"itemprop": "datePublished"}):
        return True
    meta = soup.find("meta", property="article:published_time")
    return meta is not None
