import type { CrawlLogEntry, LogDecision } from "../api/types";

const DECISION_BG: Record<LogDecision, string> = {
  saved:     "bg-green-50  border-l-green-500",
  blocked:   "bg-red-50    border-l-red-500",
  duplicate: "bg-amber-50  border-l-amber-500",
  skipped:   "bg-gray-50   border-l-gray-400",
  error:     "bg-purple-50 border-l-purple-500",
};

const LABEL_COLOR: Record<LogDecision, string> = {
  saved:     "text-green-700",
  blocked:   "text-red-700",
  duplicate: "text-amber-700",
  skipped:   "text-gray-500",
  error:     "text-purple-700",
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
      className="bg-white border border-gray-200 rounded-xl shadow-card flex flex-col overflow-hidden"
      style={{ height: 480 }}
      onMouseEnter={() => onPauseToggle(true)}
      onMouseLeave={() => onPauseToggle(false)}
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <span className={`w-2 h-2 rounded-full ${paused ? "bg-gray-300" : "bg-green-500 animate-pulse"}`} />
          <span className="text-sm font-medium text-gray-700">Live Activity</span>
        </div>
        <span className="text-xs text-gray-400">
          {paused ? "paused" : "streaming"} · {logs.length} events
        </span>
      </div>

      {/* Feed */}
      <div className="flex-1 overflow-y-auto feed-scroll">
        {logs.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-sm text-gray-400">Waiting for crawl events…</p>
          </div>
        )}
        {logs.map((entry, i) => (
          <div
            key={`${entry.url}-${i}`}
            className={`flex gap-3 px-4 py-2.5 border-b border-gray-100 border-l-2 animate-feed-slide ${DECISION_BG[entry.decision]}`}
          >
            <span className={`shrink-0 text-[10px] font-bold uppercase tracking-wider pt-0.5 w-12 ${LABEL_COLOR[entry.decision]}`}>
              {LABEL_TEXT[entry.decision]}
            </span>
            <div className="min-w-0 flex-1">
              <p className="font-mono text-xs text-gray-600 truncate">{entry.url}</p>
              {reason(entry) && (
                <p className="text-xs text-gray-400 mt-0.5">{reason(entry)}</p>
              )}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
