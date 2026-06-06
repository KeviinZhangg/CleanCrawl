import { StatsPanel } from "../components/Stats/StatsPanel";

export function DashboardPage() {
  return (
    <div className="max-w-6xl mx-auto px-8 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-0.5">Crawl statistics across all runs</p>
      </div>
      <StatsPanel />
    </div>
  );
}
