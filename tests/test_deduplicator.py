"""Tests for duplicate and near-duplicate detection."""

from pathlib import Path

import pytest

from crawler.classifier import classify_page
from crawler.deduplicator import Deduplicator, normalize_url
from crawler.extractor import extract_content
from models import ArticleContent

FIXTURES = Path(__file__).parent.parent / "fixtures"

URL_VARIANTS = [
    "https://example.com/article/ai-news",
    "https://example.com/article/ai-news?utm_source=twitter",
    "https://example.com/amp/article/ai-news",
    "https://example.com/mobile/article/ai-news",
    "https://example.com/print/article/ai-news",
]


def test_normalize_url_variants():
    normalized = [normalize_url(u) for u in URL_VARIANTS]
    assert len(set(normalized)) == 1
    assert normalized[0] == "https://example.com/article/ai-news"


def test_five_variants_one_stored():
    html = (FIXTURES / "ai_news.html").read_text()
    dedup = Deduplicator()
    stored = 0
    duplicates = 0

    for url in URL_VARIANTS:
        clf = classify_page(url, html)
        article = extract_content(url, html, clf)
        article.url = url
        result = dedup.check(article)
        if result.is_duplicate:
            duplicates += 1
        else:
            stored += 1

    assert stored == 1
    assert duplicates == 4


def test_near_duplicate_detection():
    dedup = Deduplicator()

    for name in ("near_dup_a", "near_dup_b"):
        html = (FIXTURES / f"{name}.html").read_text()
        url = f"https://example.com/article/{name}"
        clf = classify_page(url, html)
        article = extract_content(url, html, clf)
        article.url = url
        result = dedup.check(article)
        if name == "near_dup_a":
            assert not result.is_duplicate
        else:
            assert result.is_duplicate
            assert result.duplicate_reason in (
                "near_duplicate_text",
                "same_canonical_url_and_similar_text",
                "same_content_hash",
            )


def test_duplicate_json_shape():
    dedup = Deduplicator()
    html = (FIXTURES / "ai_news.html").read_text()
    article = extract_content(
        URL_VARIANTS[0], html, classify_page(URL_VARIANTS[0], html)
    )
    dedup.check(article)

    article2 = extract_content(
        URL_VARIANTS[1], html, classify_page(URL_VARIANTS[1], html)
    )
    article2.url = URL_VARIANTS[1]
    result = dedup.check(article2)
    d = result.as_dict()
    assert d["is_duplicate"] is True
    assert d["duplicate_of"]
    assert d["duplicate_reason"]
