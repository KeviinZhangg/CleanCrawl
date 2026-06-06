import { ExternalLink } from "lucide-react";
import type { Article } from "../api/types";
import { QualityBreakdown } from "./QualityBreakdown";

export function ArticleDetail({ article }: { article: Article }) {
  return (
    <div className="grid lg:grid-cols-[1fr_280px] gap-8 animate-reveal-up">
      {/* Main article */}
      <article className="space-y-5 min-w-0">
        <header className="pb-5 border-b border-gray-200">
          {article.page_type && (
            <span className="inline-block text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-md mb-3">
              {article.page_type.replace(/_/g, " ")}
            </span>
          )}
          <h1 className="text-2xl font-semibold text-gray-900 leading-snug mb-3">
            {article.title}
          </h1>
          <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500">
            {article.author        && <span>{article.author}</span>}
            {article.published_date && <span>{article.published_date}</span>}
            {article.source_domain  && <span className="font-mono text-xs">{article.source_domain}</span>}
            {article.language       && <span className="uppercase text-xs">{article.language}</span>}
          </div>
          <a
            href={article.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1 mt-2 text-xs text-indigo-500 hover:text-indigo-700 transition-colors"
          >
            <ExternalLink size={11} />
            Open original
          </a>
        </header>

        {article.summary && (
          <blockquote className="border-l-4 border-indigo-400 pl-4 py-1">
            <p className="text-gray-600 italic text-sm leading-relaxed">{article.summary}</p>
          </blockquote>
        )}

        {article.headings.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {article.headings.map((h, i) => (
              <span key={i} className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded font-mono">
                {h}
              </span>
            ))}
          </div>
        )}

        <div className="text-sm text-gray-700 leading-7 whitespace-pre-wrap">
          {article.main_content}
        </div>
      </article>

      {/* Sidebar */}
      <aside className="space-y-4">
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-card">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Quality Score</h3>
          <QualityBreakdown article={article} />
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-card space-y-3">
          <h3 className="text-sm font-semibold text-gray-700">Page Details</h3>
          <div className="flex flex-wrap gap-2">
            <span className={`text-xs font-medium px-2 py-1 rounded-md border ${
              article.html_quality === "messy"
                ? "border-orange-200 text-orange-600 bg-orange-50"
                : "border-green-200 text-green-600 bg-green-50"
            }`}>
              HTML: {article.html_quality}
            </span>
          </div>
          {article.problems_detected.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {article.problems_detected.map((p) => (
                <span key={p} className="text-xs font-mono text-gray-500 bg-gray-100 px-2 py-0.5 rounded">
                  {p}
                </span>
              ))}
            </div>
          )}
          {article.canonical_url && article.canonical_url !== article.url && (
            <p className="text-xs font-mono text-gray-400 break-all leading-relaxed">
              canonical: {article.canonical_url}
            </p>
          )}
        </div>
      </aside>
    </div>
  );
}
