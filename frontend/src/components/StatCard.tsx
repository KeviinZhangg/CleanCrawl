interface Props {
  label: string;
  value: string | number;
  sub?: string;
  accent?: string;
}

export function StatCard({ label, value, sub, accent }: Props) {
  return (
    <div className="mesh-card p-5">
      <p className="mesh-label mb-3">{label}</p>
      <p className={`text-2xl font-display font-medium tabular-nums tracking-tight ${accent ?? ""}`}
        style={{ color: accent ? undefined : "var(--mesh-text)" }}
      >
        {value}
      </p>
      {sub && <p className="text-xs mt-1.5" style={{ color: "var(--mesh-subtle)" }}>{sub}</p>}
    </div>
  );
}
