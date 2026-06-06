import { useState } from "react";
import { Link } from "react-router-dom";
import { Search } from "lucide-react";
import { useArticles } from "../api/client";

function QualityBadge({ score }: { score: number }) {
  const tier =
    score >= 0.8 ? "text-decision-saved"
    : score >= 0.6 ? "text-decision-duplicate"
    : "text-decision-blocked";
  return (
    <span className={`font-mono text-xs font-medium ${tier}`}>
      {score.toFixed(2)}
    </span>
  );
}

function domainInitials(domain: string): string {
  const parts = domain.replace("www.", "").split(".");
  return (parts[0]?.slice(0, 2) ?? "??").toUpperCase();
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
    <div className="space-y-6">
      <div className="mesh-card px-5 py-4 flex flex-wrap gap-4 items-center">
        <div className="flex items-center gap-2 flex-1 min-w-[180px]">
          <Search size={14} style={{ color: "var(--mesh-muted)" }} className="shrink-0" />
          <input
            placeholder="Search articles…"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="flex-1 text-sm focus:outline-none bg-transparent"
            style={{ color: "var(--mesh-text)" }}
          />
        </div>
        <div className="w-px h-5 hidden sm:block" style={{ background: "var(--mesh-border)" }} />
        <select
          value={pageType}
          onChange={(e) => setPageType(e.target.value)}
          className="text-sm bg-transparent focus:outline-none cursor-pointer"
          style={{ color: "var(--mesh-muted)" }}
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
          className="text-sm bg-transparent focus:outline-none cursor-pointer"
          style={{ color: "var(--mesh-muted)" }}
        >
          <option value="quality">Sort: Quality</option>
          <option value="date">Sort: Date</option>
        </select>
      </div>

      {isLoading && (
        <p className="text-sm py-12 text-center" style={{ color: "var(--mesh-muted)" }}>Loading…</p>
      )}
      {!isLoading && !articles?.length && (
        <p className="text-sm py-12 text-center" style={{ color: "var(--mesh-muted)" }}>No articles yet — start a crawl</p>
      )}

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {articles?.map((a) => (
          <Link
            key={a.id}
            to={`/articles/${a.id}`}
            className="mesh-card mesh-card-interactive overflow-hidden group"
          >
            <div className="mesh-gradient-preview h-36 flex items-center justify-center relative">
              <span className="font-display text-4xl font-light tracking-widest opacity-20 group-hover:opacity-30 transition-opacity"
                style={{ color: "var(--mesh-accent)" }}
              >
                {domainInitials(a.source_domain)}
              </span>
              <div className="absolute top-3 left-3">
                <span className="mesh-badge">{a.page_type?.replace(/_/g, " ") ?? "article"}</span>
              </div>
              <div className="absolute top-3 right-3">
                <span className={`w-2 h-2 rounded-full inline-block ${a.html_quality === "messy" ? "bg-decision-messy" : "bg-decision-saved"}`} />
              </div>
            </div>
            <div className="p-5 space-y-2">
              <h3 className="font-display text-sm font-medium leading-snug line-clamp-2 group-hover:text-mesh-accent transition-colors"
                style={{ color: "var(--mesh-text)" }}
              >
                {a.title || a.url}
              </h3>
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] uppercase tracking-wider" style={{ color: "var(--mesh-muted)" }}>
                  {a.source_domain}
                </span>
                <QualityBadge score={a.quality_score} />
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
