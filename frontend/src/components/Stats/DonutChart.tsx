import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import type { CrawlStats } from "../../api/types";

const COLORS = ["#34d399", "#f87171", "#fbbf24", "#9ca3af"];

const TOOLTIP_STYLE = {
  background: "#111111",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 12,
  fontFamily: "Inter, sans-serif",
  fontSize: 12,
  color: "#ededed",
  padding: "8px 12px",
  boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
};

export function DonutChart({ stats }: { stats: CrawlStats }) {
  const data = [
    { name: "Saved",      value: stats.saved },
    { name: "Blocked",    value: stats.blocked },
    { name: "Duplicates", value: stats.duplicates },
    { name: "Skipped",    value: stats.traps_skipped },
  ].filter((d) => d.value > 0);

  if (!data.length) return (
    <p className="text-sm py-8 text-center" style={{ color: "var(--mesh-muted)" }}>No crawl data yet</p>
  );

  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={data}
          innerRadius={55}
          outerRadius={82}
          paddingAngle={3}
          dataKey="value"
          strokeWidth={0}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelStyle={{ color: "#ededed", fontWeight: 600 }}
          itemStyle={{ color: "#888888" }}
          cursor={false}
        />
        <Legend
          iconType="circle"
          iconSize={8}
          formatter={(value) => (
            <span style={{ fontSize: 12, color: "#888888", fontFamily: "Inter, sans-serif" }}>
              {value}
            </span>
          )}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
