import { useParams, Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useArticle } from "../api/client";
import { ArticleDetail } from "../components/ArticleDetail";
import { ArticleTable } from "../components/ArticleTable";

export function ArticlePage() {
  const { id } = useParams();
  const articleId = id ? Number(id) : 0;
  const { data: article, isLoading, error } = useArticle(articleId);

  if (!id) {
    return (
      <div className="max-w-6xl mx-auto px-8 py-8">
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-gray-900">Articles</h1>
          <p className="text-sm text-gray-500 mt-0.5">Extracted, deduplicated, and quality-scored content</p>
        </div>
        <ArticleTable />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-8 py-8">
      <Link
        to="/articles"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-indigo-600 transition-colors mb-6"
      >
        <ArrowLeft size={14} />
        All Articles
      </Link>
      {isLoading && <p className="text-sm text-gray-400">Loading…</p>}
      {error && <p className="text-sm text-red-500">Article not found.</p>}
      {article && <ArticleDetail article={article} />}
    </div>
  );
}
