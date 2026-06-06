import type { CrawlLogEntry, LogDecision } from "../api/types";

const DECISION_BG: Record<LogDecision, string> = {
  saved:     "decision-bg-saved",
  blocked:   "decision-bg-blocked",
  duplicate: "decision-bg-duplicate",
  skipped:   "decision-bg-skipped",
  error:     "decision-bg-error",
};

const LABEL_COLOR: Record<LogDecision, string> = {
  saved:     "decision-saved",
  blocked:   "decision-blocked",
  duplicate: "decision-duplicate",
  skipped:   "decision-skipped",
  error:     "decision-error",
};

const LABEL_TEXT: Record<LogDecision, string> = {
  saved:     "SAVED",
  blocked:   "BLOCKED",
  duplicate: "DUP",
  skipped:   "SKIP",
  error:     "ERROR",
};

function reason(entry: CrawlLogEntry): string | null {
  if (entry.blocked_reason)    return entry.blocked_reason;
  if (entry.skip_reason)       return entry.skip_reason;
  if (entry.duplicate_reason)  return entry.duplicate_reason;
  if (entry.quality_score != null) return `quality ${entry.quality_score.toFixed(2)}`;
  return null;
}

interface Props {
  logs: CrawlLogEntry[];
  paused: boolean;
  onPauseToggle: (v: boolean) => void;
  bottomRef: React.RefObject<HTMLDivElement>;
}

export function ActivityFeed({ logs, paused, onPauseToggle, bottomRef }: Props) {
  return (
    <div
      className="mesh-card flex flex-col overflow-hidden"
      style={{ height: 480 }}
      onMouseEnter={() => onPauseToggle(true)}
      onMouseLeave={() => onPauseToggle(false)}
    >
      <div className="px-5 py-4 border-b flex items-center justify-between shrink-0"
        style={{ borderColor: "var(--mesh-border)" }}
      >
        <div className="flex items-center gap-2.5">
          <span className={`w-2 h-2 rounded-full ${paused ? "bg-mesh-subtle" : "bg-decision-saved animate-pulse"}`} />
          <span className="mesh-section-title text-sm">Live Activity</span>
        </div>
        <span className="mesh-label">
          {paused ? "paused" : "streaming"} · {logs.length} events
        </span>
      </div>

      <div className="flex-1 overflow-y-auto feed-scroll">
        {logs.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm" style={{ color: "var(--mesh-muted)" }}>Waiting for crawl events…</p>
          </div>
        )}
        {logs.map((entry, i) => (
          <div
            key={`${entry.url}-${i}`}
            className={`flex gap-3 px-5 py-3 border-b border-l-2 animate-feed-slide ${DECISION_BG[entry.decision]}`}
            style={{ borderColor: "var(--mesh-border)" }}
          >
            <span className={`shrink-0 text-[10px] font-mono font-medium uppercase tracking-wider pt-0.5 w-14 ${LABEL_COLOR[entry.decision]}`}>
              {LABEL_TEXT[entry.decision]}
            </span>
            <div className="min-w-0 flex-1">
              <p className="font-mono text-xs truncate" style={{ color: "var(--mesh-text)" }}>{entry.url}</p>
              {reason(entry) && (
                <p className="text-xs mt-0.5" style={{ color: "var(--mesh-muted)" }}>{reason(entry)}</p>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
