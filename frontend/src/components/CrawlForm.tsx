import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Play, Loader2 } from "lucide-react";
import { useStartCrawl } from "../api/client";

const DEMO_SEEDS = `fixture://clean_article
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
    <form onSubmit={handleSubmit} className="max-w-2xl space-y-5">
      {/* Textarea */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Seed URLs <span className="text-gray-400 font-normal">(one per line)</span>
        </label>
        <textarea
          value={seeds}
          onChange={(e) => setSeeds(e.target.value)}
          rows={12}
          className="w-full bg-white border border-gray-200 rounded-lg px-3 py-2.5 font-mono text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none placeholder-gray-300"
          placeholder="https://example.com/article"
        />
      </div>

      {/* Options */}
      <div className="flex items-center gap-6">
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={render}
            onChange={(e) => setRender(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
          />
          <span className="text-sm text-gray-600">JS render fallback</span>
        </label>

        <div className="flex items-center gap-2">
          <label className="text-sm text-gray-600">Max depth</label>
          <input
            type="number"
            min={0}
            max={3}
            value={maxDepth}
            onChange={(e) => setMaxDepth(Number(e.target.value))}
            className="w-14 bg-white border border-gray-200 rounded-md px-2 py-1 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={start.isPending}
        className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-medium px-5 py-2.5 rounded-lg transition-colors"
      >
        {start.isPending
          ? <Loader2 size={16} className="animate-spin" />
          : <Play size={16} />
        }
        {start.isPending ? "Starting…" : "Start Crawl"}
      </button>

      {start.isError && (
        <p className="text-sm text-red-500">{(start.error as Error).message}</p>
      )}
    </form>
  );
}
