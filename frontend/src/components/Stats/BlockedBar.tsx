import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import type { CrawlStats } from "../../api/types";

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

export function BlockedBar({ stats }: { stats: CrawlStats }) {
  const data = Object.entries(stats.blocked_by_reason).map(([reason, count]) => ({
    reason: reason.replace(/_/g, " "),
    count,
  }));

  if (!data.length) return (
    <p className="text-sm text-gray-400 py-8 text-center">No blocks recorded</p>
  );

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 16, top: 4, bottom: 4 }}>
        <XAxis
          type="number"
          tick={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 11, fill: "#9CA3AF" }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          type="category"
          dataKey="reason"
          width={100}
          tick={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 11, fill: "#6B7280" }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelStyle={{ color: "#111827", fontWeight: 600 }}
          itemStyle={{ color: "#4B5563" }}
          cursor={{ fill: "rgba(79,70,229,0.05)" }}
        />
        <Bar dataKey="count" fill="#4F46E5" radius={[0, 4, 4, 0]} barSize={18} />
      </BarChart>
    </ResponsiveContainer>
  );
}
