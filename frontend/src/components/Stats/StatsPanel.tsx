import { useStats } from "../../api/client";
import { StatCard } from "../StatCard";
import { DonutChart } from "./DonutChart";
import { BlockedBar } from "./BlockedBar";

export function StatsPanel() {
  const { data: stats, isLoading, error } = useStats();

  if (isLoading) return (
    <p className="text-sm text-gray-400">Loading statistics…</p>
  );
  if (error || !stats) return (
    <p className="text-sm text-red-500">Failed to load statistics.</p>
  );

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Success Rate"
          value={`${(stats.success_rate * 100).toFixed(1)}%`}
          accent="text-indigo-600"
        />
        <StatCard
          label="Extraction Rate"
          value={`${(stats.extraction_success_rate * 100).toFixed(0)}%`}
        />
        <StatCard
          label="Duplicates Removed"
          value={stats.duplicates}
          accent="text-amber-600"
        />
        <StatCard
          label="Traps Skipped"
          value={stats.traps_skipped}
          accent="text-gray-500"
        />
      </div>

      {/* Charts — 50/50 */}
      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-card">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Outcome Distribution</h3>
          <DonutChart stats={stats} />
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-card">
          <h3 className="text-sm font-semibold text-gray-700 mb-4">Blocked by Reason</h3>
          <BlockedBar stats={stats} />
        </div>
      </div>
    </div>
  );
}
