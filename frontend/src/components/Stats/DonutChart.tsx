import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { CrawlStats } from "../../api/types";

const COLORS = ["#059669", "#DC2626", "#D97706", "#6B7280"];
const LABELS = ["Saved", "Blocked", "Duplicates", "Skipped"];

const TOOLTIP_STYLE = {
  background: "#ffffff",
  border: "1px solid #E5E7EB",
  borderRadius: 8,
  fontFamily: "'Plus Jakarta Sans', sans-serif",
  fontSize: 12,
  color: "#111827",
  padding: "8px 12px",
  boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
};

export function DonutChart({ stats }: { stats: CrawlStats }) {
  const data = [
    { name: "Saved",      value: stats.saved },
    { name: "Blocked",    value: stats.blocked },
    { name: "Duplicates", value: stats.duplicates },
    { name: "Skipped",    value: stats.traps_skipped },
  ].filter((d) => d.value > 0);

  if (!data.length) return (
    <p className="text-sm text-gray-400 py-8 text-center">No crawl data yet</p>
  );

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={data}
          innerRadius={55}
          outerRadius={82}
          paddingAngle={2}
          dataKey="value"
          strokeWidth={0}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelStyle={{ color: "#111827", fontWeight: 600 }}
          itemStyle={{ color: "#4B5563" }}
          cursor={false}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(value) => (
            <span style={{ fontSize: 12, color: "#4B5563", fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
              {value}
            </span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
