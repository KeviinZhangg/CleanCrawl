import type { Article } from "../api/types";

const FACTOR_LABELS: Record<string, string> = {
  completeness: "Completeness",
  cleanliness:  "Cleanliness",
  usefulness:   "Usefulness",
  uniqueness:   "Uniqueness",
  freshness:    "Freshness",
};

const WEIGHTS: Record<string, number> = {
  completeness: 0.3,
  cleanliness:  0.25,
  usefulness:   0.2,
  uniqueness:   0.15,
  freshness:    0.1,
};

export function QualityBreakdown({ article }: { article: Article }) {
  const factors = article.quality_factors;

  return (
    <div className="space-y-4">
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-display font-medium tabular-nums text-mesh-accent">
          {article.quality_score.toFixed(2)}
        </span>
        <span className="text-xs" style={{ color: "var(--mesh-muted)" }}>/ 1.00</span>
      </div>

      <div className="space-y-3">
        {Object.entries(FACTOR_LABELS).map(([key, label]) => {
          const val = factors[key] ?? 0;
          const weight = WEIGHTS[key] ?? 0;
          return (
            <div key={key}>
              <div className="flex justify-between items-baseline mb-1.5">
                <span className="text-xs" style={{ color: "var(--mesh-muted)" }}>{label}</span>
                <span className="font-mono text-xs" style={{ color: "var(--mesh-subtle)" }}>
                  {val.toFixed(2)}
                  <span className="ml-0.5" style={{ color: "var(--mesh-subtle)" }}>×{weight}</span>
                </span>
              </div>
              <div className="h-1 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.06)" }}>
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{ width: `${val * 100}%`, background: "var(--mesh-accent)" }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {article.quality_reasons.length > 0 && (
        <div className="pt-4 border-t space-y-2" style={{ borderColor: "var(--mesh-border)" }}>
          {article.quality_reasons.map((r) => (
            <div key={r} className="flex gap-2 text-xs">
              <span className="text-mesh-accent shrink-0">→</span>
              <span style={{ color: "var(--mesh-muted)" }}>{r}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
