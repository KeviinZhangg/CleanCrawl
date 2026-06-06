import { useParams, Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useArticle } from "../api/client";
import { ArticleDetail } from "../components/ArticleDetail";
import { ArticleTable } from "../components/ArticleTable";
import { PageHeader } from "../components/PageHeader";

export function ArticlePage() {
  const { id } = useParams();
  const articleId = id ? Number(id) : 0;
  const { data: article, isLoading, error } = useArticle(articleId);

  if (!id) {
    return (
      <div className="max-w-7xl mx-auto px-6 md:px-10 py-10 md:py-14">
        <PageHeader
          label="Saved articles"
          title="Extracted, deduplicated,"
          accent="quality-scored content."
          subtitle="Every article includes an explainable quality breakdown."
        />
        <ArticleTable />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 md:px-10 py-10 md:py-14">
      <Link
        to="/articles"
        className="inline-flex items-center gap-1.5 text-sm mb-8 transition-colors mesh-btn-ghost !rounded-lg"
      >
        <ArrowLeft size={14} />
        All Articles
      </Link>
      {isLoading && <p className="text-sm" style={{ color: "var(--mesh-muted)" }}>Loading…</p>}
      {error && <p className="text-sm decision-blocked">Article not found.</p>}
      {article && <ArticleDetail article={article} />}
    </div>
  );
}
