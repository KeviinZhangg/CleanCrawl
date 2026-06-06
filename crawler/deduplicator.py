"""Duplicate and near-duplicate detection: canonical, URL, hash, MinHash."""

from __future__ import annotations

import hashlib
import re
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from datasketch import MinHash, MinHashLSH

import config
from models import ArticleContent, DuplicateResult

TRACKING = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "ref", "source", "gclid", "fbclid",
}
PREFIXES = ("/amp", "/mobile", "/print")


def normalize_url(u: str) -> str:
    p = urlsplit(u)
    qs = sorted((k, v) for k, v in parse_qsl(p.query) if k.lower() not in TRACKING)
    path = p.path
    for pre in PREFIXES:
        if path.startswith(pre):
            path = path[len(pre):] or "/"
    return urlunsplit(
        (p.scheme.lower(), p.netloc.lower(), path.rstrip("/") or "/", urlencode(qs), "")
    )


def content_hash(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return hashlib.sha256(normalized.encode()).hexdigest()


def _shingles(text: str, size: int = config.SHINGLE_SIZE) -> set[str]:
    words = re.sub(r"\s+", " ", text.lower()).split()
    if len(words) < size:
        return {" ".join(words)} if words else set()
    return {" ".join(words[i : i + size]) for i in range(len(words) - size + 1)}


def _title_similarity(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


class Deduplicator:
    """Four-layer dedup backed by in-memory indexes (persisted via storage layer)."""

    def __init__(self) -> None:
        self._canonicals: dict[str, str] = {}
        self._hashes: dict[str, str] = {}
        self._titles: dict[str, str] = {}
        self._dates: dict[str, str | None] = {}
        self._lsh = MinHashLSH(threshold=config.NEAR_DUP_JACCARD, num_perm=config.MINHASH_PERM)
        self._minhashes: dict[str, MinHash] = {}

    def load_from_db(self, rows: list[tuple]) -> None:
        """Restore indexes from stored articles: (url, canonical, title, date, content_hash)."""
        for url, canonical, title, date, chash in rows:
            key = normalize_url(canonical or url)
            self._canonicals[key] = url
            if chash:
                self._hashes[chash] = url
            self._titles[url] = title or ""
            self._dates[url] = date
            if chash:
                mh = self._build_minhash_from_hash_key(url, chash)
                if mh:
                    self._lsh.insert(url, mh)
                    self._minhashes[url] = mh

    def _build_minhash(self, text: str) -> MinHash:
        mh = MinHash(num_perm=config.MINHASH_PERM)
        for shingle in _shingles(text):
            mh.update(shingle.encode())
        return mh

    def _build_minhash_from_hash_key(self, url: str, _chash: str) -> MinHash | None:
        return self._minhashes.get(url)

    def max_similarity(self, article: ArticleContent) -> float:
        """Return highest Jaccard similarity to existing corpus."""
        if not article.main_content:
            return 0.0
        mh = self._build_minhash(article.main_content)
        candidates = self._lsh.query(mh)
        best = 0.0
        for cand_url in candidates:
            cand_mh = self._minhashes.get(cand_url)
            if cand_mh:
                best = max(best, mh.jaccard(cand_mh))
        return best

    def check(self, article: ArticleContent) -> DuplicateResult:
        canonical = normalize_url(article.canonical_url or article.url)

        if canonical in self._canonicals:
            return DuplicateResult(
                is_duplicate=True,
                duplicate_of=self._canonicals[canonical],
                duplicate_reason="same_canonical_url",
            )

        norm_url = normalize_url(article.url)
        if norm_url in self._canonicals and norm_url != canonical:
            return DuplicateResult(
                is_duplicate=True,
                duplicate_of=self._canonicals[norm_url],
                duplicate_reason="same_normalized_url",
            )

        if article.main_content:
            chash = content_hash(article.main_content)
            if chash in self._hashes:
                return DuplicateResult(
                    is_duplicate=True,
                    duplicate_of=self._hashes[chash],
                    duplicate_reason="same_content_hash",
                )

            mh = self._build_minhash(article.main_content)
            candidates = self._lsh.query(mh)
            for cand_url in candidates:
                cand_mh = self._minhashes.get(cand_url)
                if not cand_mh:
                    continue
                jaccard = mh.jaccard(cand_mh)
                if jaccard >= config.NEAR_DUP_JACCARD:
                    title_sim = _title_similarity(
                        article.title, self._titles.get(cand_url)
                    )
                    if title_sim >= config.TITLE_SIM_THRESHOLD:
                        reason = (
                            "same_canonical_url_and_similar_text"
                            if canonical in self._canonicals
                            else "near_duplicate_text"
                        )
                        return DuplicateResult(
                            is_duplicate=True,
                            duplicate_of=cand_url,
                            duplicate_reason=reason,
                        )

        self._register(article, canonical)
        return DuplicateResult(is_duplicate=False)

    def _register(self, article: ArticleContent, canonical: str) -> None:
        url = article.url
        self._canonicals[canonical] = url
        self._canonicals[normalize_url(url)] = url
        self._titles[url] = article.title or ""
        self._dates[url] = article.published_date
        if article.main_content:
            chash = content_hash(article.main_content)
            self._hashes[chash] = url
            mh = self._build_minhash(article.main_content)
            self._lsh.insert(url, mh)
            self._minhashes[url] = mh
