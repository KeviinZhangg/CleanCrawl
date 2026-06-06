import { ExternalLink } from "lucide-react";
import type { Article } from "../api/types";
import { QualityBreakdown } from "./QualityBreakdown";

export function ArticleDetail({ article }: { article: Article }) {
  return (
    <div className="grid lg:grid-cols-[1fr_300px] gap-8 animate-reveal-up">
      <article className="space-y-6 min-w-0">
        <header className="pb-6 border-b" style={{ borderColor: "var(--mesh-border)" }}>
          {article.page_type && (
            <span className="mesh-badge mb-4">
              {article.page_type.replace(/_/g, " ")}
            </span>
          )}
          <h1 className="font-display text-2xl md:text-3xl font-medium leading-snug mb-4 tracking-tight"
            style={{ color: "var(--mesh-text)" }}
          >
            {article.title}
          </h1>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm" style={{ color: "var(--mesh-muted)" }}>
            {article.author        && <span>{article.author}</span>}
            {article.published_date && <span>{article.published_date}</span>}
            {article.source_domain  && <span className="font-mono text-xs">{article.source_domain}</span>}
            {article.language       && <span className="uppercase text-xs">{article.language}</span>}
          </div>
          <a
            href={article.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 mt-3 text-xs text-mesh-accent hover:opacity-80 transition-opacity"
          >
            <ExternalLink size={11} />
            Open original
          </a>
        </header>

        {article.summary && (
          <blockquote className="border-l-2 pl-5 py-1" style={{ borderColor: "var(--mesh-accent)" }}>
            <p className="italic text-sm leading-relaxed" style={{ color: "var(--mesh-muted)" }}>{article.summary}</p>
          </blockquote>
        )}

        {article.headings.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {article.headings.map((h, i) => (
              <span key={i} className="mesh-badge font-mono !normal-case !tracking-normal">
                {h}
              </span>
            ))}
          </div>
        )}

        <div className="text-sm leading-7 whitespace-pre-wrap" style={{ color: "var(--mesh-text)" }}>
          {article.main_content}
        </div>
      </article>

      <aside className="space-y-4">
        <div className="mesh-card p-6">
          <p className="mesh-label mb-1">Scoring</p>
          <h3 className="mesh-section-title mb-5">Quality breakdown</h3>
          <QualityBreakdown article={article} />
        </div>

        <div className="mesh-card p-6 space-y-4">
          <p className="mesh-label mb-1">Metadata</p>
          <h3 className="mesh-section-title">Page details</h3>
          <div className="flex flex-wrap gap-2">
            <span className={`mesh-badge ${
              article.html_quality === "messy" ? "text-decision-messy" : "text-decision-saved"
            }`}>
              HTML: {article.html_quality}
            </span>
          </div>
          {article.problems_detected.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {article.problems_detected.map((p) => (
                <span key={p} className="mesh-badge font-mono !normal-case !tracking-normal">
                  {p}
                </span>
              ))}
            </div>
          )}
          {article.canonical_url && article.canonical_url !== article.url && (
            <p className="text-xs font-mono break-all leading-relaxed" style={{ color: "var(--mesh-subtle)" }}>
              canonical: {article.canonical_url}
            </p>
          )}
        </div>
      </aside>
    </div>
  );
}
