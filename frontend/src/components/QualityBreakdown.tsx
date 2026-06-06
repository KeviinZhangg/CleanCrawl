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
      {/* Score */}
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold text-indigo-600 tabular-nums">
          {article.quality_score.toFixed(2)}
        </span>
        <span className="text-xs text-gray-400">/ 1.00</span>
      </div>

      {/* Factor bars */}
      <div className="space-y-3">
        {Object.entries(FACTOR_LABELS).map(([key, label]) => {
          const val = factors[key] ?? 0;
          const weight = WEIGHTS[key] ?? 0;
          return (
            <div key={key}>
              <div className="flex justify-between items-baseline mb-1">
                <span className="text-xs text-gray-500">{label}</span>
                <span className="font-mono text-xs text-gray-400">
                  {val.toFixed(2)}
                  <span className="text-gray-300 ml-0.5">×{weight}</span>
                </span>
              </div>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-indigo-400 rounded-full transition-all duration-500"
                  style={{ width: `${val * 100}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Reasons */}
      {article.quality_reasons.length > 0 && (
        <div className="pt-3 border-t border-gray-100 space-y-1.5">
          {article.quality_reasons.map((r) => (
            <div key={r} className="flex gap-2 text-xs">
              <span className="text-indigo-400 shrink-0">→</span>
              <span className="text-gray-500">{r}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
