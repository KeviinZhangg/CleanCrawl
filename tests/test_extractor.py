"""Tests for content extraction — clean and broken HTML fixtures."""

from pathlib import Path

import pytest

from crawler.classifier import classify_page
from crawler.extractor import extract_content

FIXTURES = Path(__file__).parent.parent / "fixtures"


def test_clean_article_extraction():
    html = (FIXTURES / "clean_article.html").read_text()
    url = "https://example.com/news/ai-crawlers"
    clf = classify_page(url, html)
    article = extract_content(url, html, clf)

    assert article.title
    assert article.published_date
    assert article.main_content
    assert len(article.headings) >= 1
    assert "Home" not in (article.main_content or "")
    assert "Privacy" not in (article.main_content or "")


def test_broken_html_still_extracts():
    html = (FIXTURES / "broken_html.html").read_text()
    url = "https://example.com/blog/broken-page"
    clf = classify_page(url, html)
    article = extract_content(url, html, clf)

    assert article.main_content
    assert len(article.main_content.split()) > 50
    assert article.html_quality == "messy"


def test_canonical_url_extracted():
    html = (FIXTURES / "clean_article.html").read_text()
    url = "https://example.com/news/ai-crawlers"
    clf = classify_page(url, html)
    article = extract_content(url, html, clf)
    assert article.canonical_url == "https://example.com/news/ai-crawlers"


def test_summary_generated():
    html = (FIXTURES / "clean_article.html").read_text()
    url = "https://example.com/news/ai-crawlers"
    clf = classify_page(url, html)
    article = extract_content(url, html, clf)
    assert article.summary
    assert len(article.summary) > 20
