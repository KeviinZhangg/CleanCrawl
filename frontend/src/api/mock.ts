import type { Article, CrawlJob, CrawlLogEntry, CrawlStats } from "./types";

export const mockStats: CrawlStats = {
  attempted: 13,
  saved: 5,
  blocked: 1,
  duplicates: 5,
  traps_skipped: 2,
  success_rate: 0.385,
  extraction_success_rate: 1.0,
  avg_quality: 0.66,
  blocked_by_reason: { cloudflare_detected: 1 },
  by_domain: {
    "en.wikipedia.org": { saved: 1, blocked: 0 },
    "example.com": { saved: 4, blocked: 1 },
  },
};

export const mockLogs: CrawlLogEntry[] = [
  { url: "fixture://clean_article", decision: "saved", status: 200, blocked_reason: null, skip_reason: null, quality_score: 0.89, timestamp: new Date().toISOString() },
  { url: "fixture://cloudflare", decision: "blocked", status: 200, blocked_reason: "cloudflare_detected", skip_reason: null, quality_score: null, timestamp: new Date().toISOString() },
  { url: "https://example.com/article/ai-news?utm_source=twitter", decision: "duplicate", status: 200, blocked_reason: null, skip_reason: null, duplicate_reason: "same_canonical_url", quality_score: null, timestamp: new Date().toISOString() },
  { url: "https://example.com/archive/2021/05/page/400", decision: "skipped", status: 0, blocked_reason: null, skip_reason: "pagination_depth_too_high", quality_score: null, timestamp: new Date().toISOString() },
];

export const mockArticles: Article[] = [
  {
    id: 1,
    url: "https://example.com/news/ai-crawlers",
    canonical_url: "https://example.com/news/ai-crawlers",
    title: "How AI Crawlers Are Changing the Web",
    author: "Jane Smith",
    published_date: "2026-06-01",
    page_type: "news_article",
    language: "en",
    summary: "The article explains how AI crawlers are affecting publishers.",
    main_content: "Artificial intelligence systems depend on large volumes of high-quality text...",
    headings: ["The Rise of Automated Content Collection", "What Publishers Are Doing"],
    images: [],
    source_domain: "example.com",
    quality_score: 0.89,
    quality_factors: { completeness: 0.9, cleanliness: 0.85, usefulness: 0.88, uniqueness: 1.0, freshness: 1.0 },
    quality_reasons: [],
    html_quality: "ok",
    problems_detected: [],
    is_duplicate: false,
    duplicate_of: null,
  },
];

export const mockJob: CrawlJob = {
  id: "demo01",
  seeds: ["fixture://clean_article"],
  status: "done",
  started_at: new Date().toISOString(),
  finished_at: new Date().toISOString(),
  stats: mockStats,
};
