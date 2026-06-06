"""Tests for explainable quality scoring."""

from crawler.quality import apply_quality, score_quality
from models import ArticleContent


def _good_article() -> ArticleContent:
    return ArticleContent(
        url="https://example.com/news/good",
        title="Complete Article",
        author="Jane Smith",
        published_date="2026-06-01",
        main_content=" ".join(["content"] * 400),
        headings=["Intro", "Details", "Conclusion"],
        html_quality="ok",
        problems_detected=[],
    )


def _poor_article() -> ArticleContent:
    return ArticleContent(
        url="https://example.com/news/poor",
        title="Thin Page",
        main_content="short text only",
        html_quality="messy",
        problems_detected=["missing_author", "missing_date", "broken_html", "used_fallback_extractor"],
    )


def test_high_quality_article():
    score, factors, reasons = score_quality(_good_article(), max_similarity=0.0)
    assert score >= 0.8
    assert "completeness" in factors
    assert factors["completeness"] >= 0.6


def test_low_quality_article():
    score, factors, reasons = score_quality(_poor_article(), max_similarity=0.9)
    assert score < 0.6
    assert len(reasons) >= 2


def test_explainable_reasons():
    score, factors, reasons = score_quality(_poor_article(), max_similarity=0.9)
    assert any("missing" in r or "stale" in r or "overlaps" in r or "noisy" in r for r in reasons)


def test_apply_quality_mutates_article():
    article = _good_article()
    apply_quality(article, 0.0)
    assert article.quality_score >= 0.8
    assert article.quality_factors
    assert isinstance(article.quality_reasons, list)
