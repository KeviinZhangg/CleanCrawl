"""Clean article content extraction with messy-HTML resilience."""

from __future__ import annotations

import json
import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, Tag

import config
from models import ArticleContent, PageClassification

NOISE_SELECTORS = [
    "nav", "footer", "header", ".cookie", ".newsletter", ".popup",
    ".ad", ".ads", ".advertisement", ".social-share", ".comments",
    ".related-articles", ".sidebar", "#comments",
]


def extract_content(
    url: str, html: str, classification: PageClassification
) -> ArticleContent:
    """Extract clean article fields, stripping noise."""
    domain = urlparse(url).netloc
    problems: list[str] = []
    extractor_used = "trafilatura"

    extracted_json = None
    try:
        import trafilatura

        extracted_json = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
            favor_recall=True,
            with_metadata=True,
            output_format="json",
        )
    except Exception:
        problems.append("trafilatura_error")

    title = author = published_date = language = main_content = None
    canonical = None

    if extracted_json:
        data = json.loads(extracted_json)
        title = data.get("title")
        author = data.get("author")
        published_date = data.get("date")
        language = data.get("language")
        main_content = data.get("text")
        canonical = data.get("url")
    else:
        problems.append("used_fallback_extractor")
        title, author, published_date, main_content, language = _readability_fallback(
            html, url
        )
        if not main_content:
            problems.append("readability_failed")
            title, main_content = _bs4_fallback(html)
            extractor_used = "beautifulsoup"

    soup = BeautifulSoup(html, "lxml")
    if not canonical:
        canonical = _extract_canonical(soup) or url
    if not title:
        title = _extract_title_fallback(soup)

    headings = [
        h.get_text(strip=True)
        for h in soup.find_all(["h1", "h2", "h3"])[:10]
        if h.get_text(strip=True)
    ]
    images = _extract_images(soup, url)

    # Noise removal pass on main_content
    if main_content:
        main_content = _strip_noise_from_text(main_content, soup)
    else:
        problems.append("empty_body")

    if not author:
        problems.append("missing_author")
    if not published_date:
        problems.append("missing_date")
    if not soup.find("article") and not soup.find("main"):
        problems.append("large_navigation_noise")

    # Detect broken HTML
    if _has_broken_html(html):
        problems.append("broken_html")

    if "cookie" in html.lower() or soup.find(class_=re.compile(r"cookie", re.I)):
        problems.append("cookie_banner_removed")

    if extractor_used != "trafilatura":
        problems.append("used_fallback_extractor")

    summary = _make_summary(main_content)
    html_quality = "messy" if len(problems) >= 2 else "ok"

    return ArticleContent(
        url=url,
        canonical_url=canonical,
        title=title,
        author=author,
        published_date=published_date,
        language=language or _detect_language(main_content),
        main_content=main_content,
        summary=summary,
        headings=headings,
        images=images,
        source_domain=domain,
        page_type=classification.page_type,
        html_quality=html_quality,
        problems_detected=problems,
    )


def img_src(tag: Tag) -> str | None:
    # why: lazy-loaded images keep the real URL in data-* and use a placeholder in src
    for attr in ("src", "data-src", "data-lazy-src", "data-original", "srcset"):
        v = tag.get(attr)
        if v:
            return v.split()[0] if attr == "srcset" else v
    return None


def _extract_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    images: list[str] = []
    seen: set[str] = set()

    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        src = urljoin(base_url, og["content"])
        images.append(src)
        seen.add(src)

    for container in soup.find_all(["article", "main", "figure"]):
        for img in container.find_all("img"):
            src = img_src(img)
            if not src or src.startswith("data:"):
                continue
            full = urljoin(base_url, src)
            if full in seen:
                continue
            w = img.get("width")
            h = img.get("height")
            if w and h:
                try:
                    if int(w) < 100 or int(h) < 100:
                        continue
                except ValueError:
                    pass
            cls = " ".join(img.get("class", [])).lower()
            if any(x in cls for x in ("icon", "logo", "avatar", "pixel", "tracking")):
                continue
            images.append(full)
            seen.add(full)

    return images[:10]


def _extract_canonical(soup: BeautifulSoup) -> str | None:
    link = soup.find("link", rel="canonical")
    return link.get("href") if link else None


def _extract_title_fallback(soup: BeautifulSoup) -> str | None:
    og = soup.find("meta", property="og:title")
    if og:
        return og.get("content")
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return soup.title.string if soup.title else None


def _readability_fallback(html: str, url: str) -> tuple:
    try:
        from readability import Document

        doc = Document(html, url=url)
        title = doc.title()
        content_html = doc.summary()
        soup = BeautifulSoup(content_html, "lxml")
        text = soup.get_text(" ", strip=True)
        return title, None, None, text, None
    except Exception:
        return None, None, None, None, None


def _bs4_fallback(html: str) -> tuple[str | None, str | None]:
    soup = BeautifulSoup(html, "lxml")
    title = _extract_title_fallback(soup)
    blocks = []
    for tag in soup.find_all(["p", "div", "section"]):
        t = tag.get_text(" ", strip=True)
        if len(t.split()) > 30:
            blocks.append(t)
    body = max(blocks, key=len) if blocks else soup.get_text(" ", strip=True)[:5000]
    return title, body


def _strip_noise_from_text(text: str, soup: BeautifulSoup) -> str:
    for sel in NOISE_SELECTORS:
        for el in soup.select(sel):
            noise = el.get_text(" ", strip=True)
            if noise and len(noise) < len(text) * 0.3:
                text = text.replace(noise, "")
    return re.sub(r"\s+", " ", text).strip()


def _make_summary(text: str | None) -> str | None:
    if not text:
        return None
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    summary = " ".join(sentences[:2])
    if len(summary) > 400:
        summary = summary[:397] + "..."
    return summary


def _detect_language(text: str | None) -> str | None:
    if not text or len(text) < 20:
        return None
    try:
        import langid

        lang, _ = langid.classify(text)
        return lang
    except Exception:
        return "en"


def _has_broken_html(html: str) -> bool:
    open_tags = len(re.findall(r"<[a-zA-Z][^/>]*(?<!/)>", html))
    close_tags = len(re.findall(r"</[a-zA-Z][^>]*>", html))
    return abs(open_tags - close_tags) > 5
