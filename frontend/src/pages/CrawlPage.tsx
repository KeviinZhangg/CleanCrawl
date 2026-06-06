import { useParams } from "react-router-dom";
import { CrawlForm } from "../components/CrawlForm";
import { LiveCrawl } from "../components/LiveCrawl";

export function CrawlPage() {
  const { jobId } = useParams();

  if (jobId) {
    return (
      <div className="max-w-6xl mx-auto px-8 py-8">
        <LiveCrawl jobId={jobId} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-8 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-gray-900">New Crawl</h1>
        <p className="text-sm text-gray-500 mt-0.5">Paste seed URLs and watch decisions stream live</p>
      </div>
      <CrawlForm />
    </div>
  );
}
