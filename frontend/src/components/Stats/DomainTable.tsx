import type { CrawlStats } from "../../api/types";

export function DomainTable({ stats }: { stats: CrawlStats }) {
  const rows = Object.entries(stats.by_domain);

  if (!rows.length) return (
    <p className="text-sm" style={{ color: "var(--mesh-muted)" }}>No domain data</p>
  );

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b" style={{ borderColor: "var(--mesh-border)" }}>
          <th className="pb-3 text-left mesh-label">Domain</th>
          <th className="pb-3 text-right mesh-label">Saved</th>
          <th className="pb-3 text-right mesh-label">Blocked</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([domain, d]) => (
          <tr key={domain} className="border-b transition-colors hover:bg-white/[0.02]"
            style={{ borderColor: "var(--mesh-border)" }}
          >
            <td className="py-3 font-mono text-xs truncate max-w-[240px]" style={{ color: "var(--mesh-text)" }}>{domain}</td>
            <td className="py-3 text-right font-medium text-decision-saved">{d.saved}</td>
            <td className="py-3 text-right font-medium text-decision-blocked">{d.blocked}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
