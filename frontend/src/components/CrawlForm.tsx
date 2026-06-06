import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Play, Loader2 } from "lucide-react";
import { useStartCrawl } from "../api/client";

const DEMO_SEEDS = `https://www.bbc.com/news/technology
https://arstechnica.com/information-technology/
https://blog.python.org
https://blog.python.org/2024/01/python-313-released.html
https://martinfowler.com/articles/microservices.html
https://www.bbc.com/news/technology?page=50
https://arstechnica.com/tag/artificial-intelligence/
https://www.investopedia.com/terms/i/inflation.asp
https://www.investopedia.com/terms/s/stockmarket.asp
https://www.investopedia.com/terms/r/recession.asp
fixture://clean_article
fixture://broken_html
fixture://category_page
fixture://cloudflare
fixture://near_dup_a
fixture://near_dup_b
https://example.com/article/ai-news
https://example.com/article/ai-news?utm_source=twitter
https://example.com/amp/article/ai-news
https://example.com/archive/2021/05/page/400`;

export function CrawlForm() {
  const [seeds, setSeeds]       = useState(DEMO_SEEDS);
  const [render, setRender]     = useState(false);
  const [maxDepth, setMaxDepth] = useState(0);
  const navigate = useNavigate();
  const start = useStartCrawl();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const lines = seeds
      .split("\n")
      .map((s) => s.trim())
      .filter((s) => s && !s.startsWith("#"));
    if (!lines.length) return;
    const job = await start.mutateAsync({
      seeds: lines,
      options: { render, max_depth: maxDepth },
    });
    navigate(`/crawl/${job.id}`);
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl space-y-6 animate-reveal-up">
      <div className="mesh-card p-6 space-y-4">
        <div>
          <label className="mesh-label block mb-3">
            Seed URLs <span style={{ color: "var(--mesh-subtle)" }}>— one per line</span>
          </label>
          <textarea
            value={seeds}
            onChange={(e) => setSeeds(e.target.value)}
            rows={12}
            className="mesh-input resize-none"
            placeholder="https://example.com/article"
          />
        </div>

        <div className="flex items-center gap-8 pt-2">
          <label className="flex items-center gap-2.5 cursor-pointer">
            <input
              type="checkbox"
              checked={render}
              onChange={(e) => setRender(e.target.checked)}
              className="w-4 h-4 rounded border-mesh-border bg-mesh-surface accent-mesh-accent"
            />
            <span className="text-sm" style={{ color: "var(--mesh-muted)" }}>JS render fallback</span>
          </label>

          <div className="flex items-center gap-2">
            <label className="text-sm" style={{ color: "var(--mesh-muted)" }}>Max depth</label>
            <input
              type="number"
              min={0}
              max={3}
              value={maxDepth}
              onChange={(e) => setMaxDepth(Number(e.target.value))}
              className="w-14 mesh-input !py-1.5 text-center !px-2"
            />
          </div>
        </div>
      </div>

      <button type="submit" disabled={start.isPending} className="mesh-btn-primary">
        {start.isPending
          ? <Loader2 size={16} className="animate-spin" />
          : <Play size={16} />
        }
        {start.isPending ? "Starting…" : "Start Crawl"}
      </button>

      {start.isError && (
        <p className="text-sm decision-blocked">{(start.error as Error).message}</p>
      )}
    </form>
  );
}
