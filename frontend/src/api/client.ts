import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Article, CrawlJob, CrawlLogEntry, CrawlOptions, CrawlStats } from "./types";
import { mockArticles, mockJob, mockLogs, mockStats } from "./mock";

const USE_MOCK = import.meta.env.VITE_USE_MOCK === "true";
const BASE = "/api";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function useStats() {
  return useQuery({
    queryKey: ["stats"],
    queryFn: () => (USE_MOCK ? Promise.resolve(mockStats) : fetchJson<CrawlStats>("/stats")),
    refetchInterval: 5000,
  });
}

export function useArticles(params: Record<string, string | number | undefined>) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== "") qs.set(k, String(v));
  });
  return useQuery({
    queryKey: ["articles", params],
    queryFn: () =>
      USE_MOCK
        ? Promise.resolve(mockArticles)
        : fetchJson<Article[]>(`/articles?${qs}`),
  });
}

export function useArticle(id: number) {
  return useQuery({
    queryKey: ["article", id],
    queryFn: () =>
      USE_MOCK
        ? Promise.resolve(mockArticles[0])
        : fetchJson<Article>(`/articles/${id}`),
    enabled: id > 0,
  });
}

export function useCrawlJob(id: string | undefined) {
  return useQuery({
    queryKey: ["crawl", id],
    queryFn: () =>
      USE_MOCK ? Promise.resolve(mockJob) : fetchJson<CrawlJob>(`/crawls/${id}`),
    enabled: !!id,
    refetchInterval: (q) => (q.state.data?.status === "running" ? 2000 : false),
  });
}

export function useStartCrawl() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { seeds: string[]; options: CrawlOptions }) =>
      USE_MOCK
        ? Promise.resolve({ ...mockJob, id: "mock-" + Date.now(), status: "running" as const })
        : fetchJson<CrawlJob>("/crawls", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
          }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["stats"] }),
  });
}

export async function fetchCrawlLog(jobId: string): Promise<CrawlLogEntry[]> {
  if (USE_MOCK) return mockLogs;
  return fetchJson(`/crawls/${jobId}/log`);
}
