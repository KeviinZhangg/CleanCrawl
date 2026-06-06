import { StatsPanel } from "../components/Stats/StatsPanel";
import { PageHeader } from "../components/PageHeader";

export function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto px-6 md:px-10 py-10 md:py-14">
      <PageHeader
        label="Crawl statistics"
        title="A live overview of"
        accent="every crawling decision."
        subtitle="Saved, blocked, duplicated, and skipped — each with an explainable reason."
      />
      <StatsPanel />
    </div>
  );
}
