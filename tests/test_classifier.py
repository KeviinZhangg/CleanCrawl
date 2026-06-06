"""Tests for page classifier — spec useful vs not-useful examples."""

import pytest
from crawler.classifier import classify_page

USEFUL = [
    ("/news/2026/ai-regulation-explained", True),
    ("/blog/how-search-engines-work", True),
    ("/wiki/Web_crawler", True),
    ("/docs/crawling-best-practices", True),
]

NOT_USEFUL = [
    ("/tag/ai", False),
    ("/category/news", False),
    ("/search?q=crawler", False),
    ("/login", False),
    ("/author/john", False),
    ("/page/20", False),
]

MINIMAL_ARTICLE_HTML = """
<html><body><article itemtype="http://schema.org/NewsArticle">
<h1>Test Article Title Here</h1>
<p class="byline">By Author Name</p>
<time datetime="2026-06-01">June 1, 2026</time>
<p>""" + " ".join(["word"] * 300) + """</p>
</article></body></html>
"""

MINIMAL_LISTING_HTML = """
<html><body><nav>""" + "".join(f'<a href="/item{i}">Link</a>' for i in range(120)) + """</nav>
<h1>Category Page</h1><ul><li>Item</li></ul></body></html>
"""


@pytest.mark.parametrize("path,expected", USEFUL)
def test_useful_url_patterns(path, expected):
    url = f"https://example.com{path}"
    result = classify_page(url, MINIMAL_ARTICLE_HTML)
    assert result.is_content_page == expected
    assert 0.0 <= result.confidence <= 1.0


@pytest.mark.parametrize("path,expected", NOT_USEFUL)
def test_not_useful_url_patterns(path, expected):
    url = f"https://example.com{path}"
    html = MINIMAL_LISTING_HTML if "page" in path or "category" in path else "<html><body><p>short</p></body></html>"
    result = classify_page(url, html)
    assert result.is_content_page == expected
    assert result.confidence >= 0.0


def test_homepage_skipped():
    result = classify_page("https://example.com/", MINIMAL_ARTICLE_HTML)
    assert result.is_content_page is False
    assert result.skip_reason == "homepage"


def test_confidence_in_range():
    result = classify_page("https://example.com/news/test", MINIMAL_ARTICLE_HTML)
    assert 0.0 <= result.confidence <= 1.0
