"""Explainable quality scoring with per-factor breakdown."""

from __future__ import annotations

from datetime import datetime, timezone

import config
from models import ArticleContent


def score_quality(
    article: ArticleContent, max_similarity: float = 0.0
) -> tuple[float, dict[str, float], list[str]]:
    """Return (score, factor_breakdown, human_readable_reasons)."""
    f = {
        "completeness": completeness(article),
        "cleanliness": cleanliness(article),
        "usefulness": usefulness(article),
        "uniqueness": 1.0 - max_similarity,
        "freshness": freshness(article.published_date),
    }
    score = sum(config.QUALITY_WEIGHTS[k] * v for k, v in f.items())
    reasons: list[str] = []
    if f["completeness"] < 0.6:
        reasons.append("missing author/date or short body")
    if f["cleanliness"] < 0.6:
        reasons.append("noisy HTML / boilerplate detected")
    if f["freshness"] < 0.3:
        reasons.append("stale or undated")
    if f["uniqueness"] < 0.5:
        reasons.append("overlaps existing content")
    if f["usefulness"] < 0.5:
        reasons.append("thin or poorly structured content")
    return round(score, 2), {k: round(v, 2) for k, v in f.items()}, reasons


def completeness(article: ArticleContent) -> float:
    fields = 0.0
    total = 5.0
    if article.title:
        fields += 1
    if article.author:
        fields += 1
    if article.published_date:
        fields += 1
    if article.main_content and len(article.main_content.split()) >= config.MIN_ARTICLE_WORDS // 2:
        fields += 1
    if article.headings:
        fields += 1
    return fields / total


def cleanliness(article: ArticleContent) -> float:
    score = 1.0
    penalty = 0.08
    for problem in article.problems_detected:
        score -= penalty
    if article.html_quality == "messy":
        score -= 0.15
    if article.main_content:
        words = len(article.main_content.split())
        if words > 0:
            # Penalize very short content relative to expected article length
            ratio = min(words / config.MIN_ARTICLE_WORDS, 1.0)
            score = score * (0.5 + 0.5 * ratio)
    return max(0.0, min(1.0, score))


def usefulness(article: ArticleContent) -> float:
    if not article.main_content:
        return 0.0
    words = len(article.main_content.split())
    word_score = min(words / 1000, 1.0) * 0.6
    heading_score = min(len(article.headings) / 5, 1.0) * 0.2
    para_count = article.main_content.count("\n") + article.main_content.count(". ")
    para_score = min(para_count / 10, 1.0) * 0.2
    return min(1.0, word_score + heading_score + para_score)


def freshness(published_date: str | None) -> float:
    if not published_date:
        return 0.2
    try:
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
            try:
                dt = datetime.strptime(published_date[:19], fmt).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        else:
            return 0.3
        days = (datetime.now(timezone.utc) - dt).days
        if days < 0:
            return 1.0
        if days <= 7:
            return 1.0
        if days <= 30:
            return 0.8
        if days <= 90:
            return 0.6
        if days <= 365:
            return 0.4
        return 0.2
    except Exception:
        return 0.3


def apply_quality(article: ArticleContent, max_similarity: float = 0.0) -> ArticleContent:
    score, factors, reasons = score_quality(article, max_similarity)
    article.quality_score = score
    article.quality_factors = factors
    article.quality_reasons = reasons
    return article
