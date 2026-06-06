import { useStats } from "../../api/client";
import { StatCard } from "../StatCard";
import { DonutChart } from "./DonutChart";
import { BlockedBar } from "./BlockedBar";
import { DomainTable } from "./DomainTable";

export function StatsPanel() {
  const { data: stats, isLoading, error } = useStats();

  if (isLoading) return (
    <p className="text-sm" style={{ color: "var(--mesh-muted)" }}>Loading statistics…</p>
  );
  if (error || !stats) return (
    <p className="text-sm decision-blocked">Failed to load statistics.</p>
  );

  return (
    <div className="space-y-8 animate-reveal-up">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Success Rate"
          value={`${(stats.success_rate * 100).toFixed(1)}%`}
          accent="text-mesh-accent"
        />
        <StatCard
          label="Extraction Rate"
          value={`${(stats.extraction_success_rate * 100).toFixed(0)}%`}
        />
        <StatCard
          label="Duplicates Removed"
          value={stats.duplicates}
          accent="text-decision-duplicate"
        />
        <StatCard
          label="Traps Skipped"
          value={stats.traps_skipped}
          accent="text-decision-skipped"
        />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="mesh-card p-6">
          <p className="mesh-label mb-1">Distribution</p>
          <h3 className="mesh-section-title mb-5">Outcome breakdown</h3>
          <DonutChart stats={stats} />
        </div>
        <div className="mesh-card p-6">
          <p className="mesh-label mb-1">Anti-bot</p>
          <h3 className="mesh-section-title mb-5">Blocked by reason</h3>
          <BlockedBar stats={stats} />
        </div>
      </div>

      {Object.keys(stats.by_domain).length > 0 && (
        <div className="mesh-card p-6">
          <p className="mesh-label mb-1">Per domain</p>
          <h3 className="mesh-section-title mb-5">Domain breakdown</h3>
          <DomainTable stats={stats} />
        </div>
      )}
    </div>
  );
}
