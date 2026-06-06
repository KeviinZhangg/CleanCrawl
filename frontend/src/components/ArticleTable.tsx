import { useState } from "react";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";
import { useArticles } from "../api/client";

function QualityBadge({ score }: { score: number }) {
  const cls =
    score >= 0.8 ? "bg-green-50 text-green-700"
    : score >= 0.6 ? "bg-amber-50 text-amber-700"
    : "bg-red-50 text-red-700";
  return (
    <span className={`inline-block font-mono text-xs font-medium px-2 py-0.5 rounded-md ${cls}`}>
      {score.toFixed(2)}
    </span>
  );
}

export function ArticleTable() {
  const [q, setQ]               = useState("");
  const [pageType, setPageType] = useState("");
  const [minQuality, setMinQuality] = useState("");
  const [sort, setSort]         = useState("quality");

  const { data: articles, isLoading } = useArticles({
    q:           q || undefined,
    page_type:   pageType || undefined,
    min_quality: minQuality ? Number(minQuality) : undefined,
    sort,
  });

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 shadow-card flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2 flex-1 min-w-[180px]">
          <Search size={14} className="text-gray-400 shrink-0" />
          <input
            placeholder="Search articles…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="flex-1 text-sm text-gray-700 placeholder-gray-400 focus:outline-none bg-transparent"
          />
        </div>
        <div className="w-px h-5 bg-gray-200" />
        <select
          value={pageType}
          onChange={(e) => setPageType(e.target.value)}
          className="text-sm text-gray-600 bg-transparent focus:outline-none cursor-pointer"
        >
          <option value="">All types</option>
          <option value="news_article">News</option>
          <option value="blog_post">Blog</option>
          <option value="wiki">Wiki</option>
          <option value="educational">Educational</option>
        </select>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="text-sm text-gray-600 bg-transparent focus:outline-none cursor-pointer"
        >
          <option value="quality">Sort: Quality</option>
          <option value="date">Sort: Date</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Title</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Domain</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Date</th>
              <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">Quality</th>
              <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wide">HTML</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading && (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-sm text-gray-400">Loading…</td></tr>
            )}
            {!isLoading && !articles?.length && (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-sm text-gray-400">No articles yet — start a crawl</td></tr>
            )}
            {articles?.map((a) => (
              <tr key={a.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-4 py-3">
                  <Link to={`/articles/${a.id}`} className="text-gray-800 hover:text-indigo-600 transition-colors line-clamp-1 font-medium">
                    {a.title || a.url}
                  </Link>
                </td>
                <td className="px-4 py-3 font-mono text-xs text-gray-500">{a.source_domain}</td>
                <td className="px-4 py-3 text-xs text-gray-500 capitalize">{a.page_type?.replace(/_/g, " ")}</td>
                <td className="px-4 py-3 text-xs text-gray-500">{a.published_date ?? "—"}</td>
                <td className="px-4 py-3 text-right"><QualityBadge score={a.quality_score} /></td>
                <td className="px-4 py-3 text-center">
                  <span
                    className={`inline-block w-2 h-2 rounded-full ${a.html_quality === "messy" ? "bg-orange-400" : "bg-green-500"}`}
                    title={a.html_quality}
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
