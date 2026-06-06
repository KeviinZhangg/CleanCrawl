import { useParams } from "react-router-dom";
import { CrawlForm } from "../components/CrawlForm";
import { LiveCrawl } from "../components/LiveCrawl";
import { PageHeader } from "../components/PageHeader";

export function CrawlPage() {
  const { jobId } = useParams();

  if (jobId) {
    return (
      <div className="max-w-7xl mx-auto px-6 md:px-10 py-10 md:py-14">
        <LiveCrawl jobId={jobId} />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-6 md:px-10 py-10 md:py-14">
      <PageHeader
        label="New crawl"
        title="Paste seeds,"
        accent="watch decisions stream."
        subtitle="Trap checks, bot detection, dedup, and quality scoring — visible in real time."
      />
      <CrawlForm />
    </div>
  );
}
