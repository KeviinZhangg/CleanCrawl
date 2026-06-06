import type { CrawlStats } from "../../api/types";

export function DomainTable({ stats }: { stats: CrawlStats }) {
  const rows = Object.entries(stats.by_domain);

  if (!rows.length) return (
    <p className="text-sm text-gray-400">No domain data</p>
  );

  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="border-b border-gray-200">
          <th className="pb-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wide">Domain</th>
          <th className="pb-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">Saved</th>
          <th className="pb-2 text-right text-xs font-medium text-gray-500 uppercase tracking-wide">Blocked</th>
        </tr>
      </thead>
      <tbody>
        {rows.map(([domain, d]) => (
          <tr key={domain} className="border-b border-gray-100 hover:bg-gray-50 transition-colors">
            <td className="py-2.5 font-mono text-xs text-gray-700 truncate max-w-[240px]">{domain}</td>
            <td className="py-2.5 text-right font-semibold text-decision-saved">{d.saved}</td>
            <td className="py-2.5 text-right font-semibold text-decision-blocked">{d.blocked}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
