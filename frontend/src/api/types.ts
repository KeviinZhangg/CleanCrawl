export type CrawlStatus = "queued" | "running" | "done" | "error";
export type LogDecision = "saved" | "blocked" | "duplicate" | "skipped" | "error";

export interface CrawlStats {
  attempted: number;
  saved: number;
  blocked: number;
  duplicates: number;
  traps_skipped: number;
  success_rate: number;
  extraction_success_rate: number;
  avg_quality: number;
  blocked_by_reason: Record<string, number>;
  by_domain: Record<string, { saved: number; blocked: number }>;
}

export interface CrawlJob {
  id: string;
  seeds: string[];
  status: CrawlStatus;
  started_at: string;
  finished_at: string | null;
  stats: CrawlStats;
}

export interface CrawlOptions {
  render: boolean;
  max_depth: number;
}

export interface Article {
  id: number;
  url: string;
  canonical_url: string | null;
  title: string | null;
  author: string | null;
  published_date: string | null;
  page_type: string | null;
  language: string | null;
  summary: string | null;
  main_content: string | null;
  headings: string[];
  images: string[];
  source_domain: string | null;
  quality_score: number;
  quality_factors: Record<string, number>;
  quality_reasons: string[];
  html_quality: "ok" | "messy";
  problems_detected: string[];
  is_duplicate: boolean;
  duplicate_of: string | null;
}

export interface CrawlLogEntry {
  url: string;
  decision: LogDecision;
  status: number;
  blocked_reason: string | null;
  skip_reason: string | null;
  duplicate_reason?: string | null;
  quality_score: number | null;
  timestamp: string;
}

export type CrawlEvent =
  | { type: "log"; data: CrawlLogEntry }
  | { type: "stats"; data: CrawlStats }
  | { type: "done"; data: CrawlJob }
  | { type: "error"; data: { message: string } };
