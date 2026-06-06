import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import type { CrawlStats } from "../../api/types";

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

export function BlockedBar({ stats }: { stats: CrawlStats }) {
  const data = Object.entries(stats.blocked_by_reason).map(([reason, count]) => ({
    reason: reason.replace(/_/g, " "),
    count,
  }));

  if (!data.length) return (
    <p className="text-sm py-8 text-center" style={{ color: "var(--mesh-muted)" }}>No blocks recorded</p>
  );

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
        <XAxis
          type="number"
          tick={{ fontFamily: "Inter, sans-serif", fontSize: 11, fill: "#555555" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="reason"
          width={100}
          tick={{ fontFamily: "Inter, sans-serif", fontSize: 11, fill: "#888888" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelStyle={{ color: "#ededed", fontWeight: 600 }}
          itemStyle={{ color: "#888888" }}
          cursor={{ fill: "rgba(168,180,255,0.06)" }}
        />
        <Bar dataKey="count" fill="#a8b4ff" radius={[0, 4, 4, 0]} barSize={18} />
      </BarChart>
    </ResponsiveContainer>
  );
}
