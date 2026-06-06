import { Link } from "react-router-dom";
import { CheckCircle, Wifi, WifiOff } from "lucide-react";
import { useCrawlJob } from "../api/client";
import { useCrawlEvents } from "../hooks/useCrawlEvents";
import { ActivityFeed } from "./ActivityFeed";
import { StatCard } from "./StatCard";
import type { CrawlStats } from "../api/types";

const emptyStats: CrawlStats = {
  attempted: 0, saved: 0, blocked: 0, duplicates: 0, traps_skipped: 0,
  success_rate: 0, extraction_success_rate: 0, avg_quality: 0,
  blocked_by_reason: {}, by_domain: {},
};

interface Props { jobId: string }

export function LiveCrawl({ jobId }: Props) {
  const { data: job } = useCrawlJob(jobId);
  const { logs, stats, status, paused, setPaused, bottomRef } = useCrawlEvents(
    jobId,
    job?.status === "running" || job?.status === "queued"
  );
  const s = stats ?? job?.stats ?? emptyStats;
  const done = status === "done" || job?.status === "done";
  const isLive = status === "live";
  const isError = status === "error";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Crawl #{jobId}</h1>
          <div className="flex items-center gap-2 mt-1">
            <span className={`w-2 h-2 rounded-full ${isLive ? "bg-green-500 animate-pulse" : isError ? "bg-red-500" : "bg-gray-400"}`} />
            <span className="text-sm text-gray-500">
              {job?.status ?? status}
              {isLive && <Wifi size={13} className="inline ml-1.5 text-green-500" />}
              {isError && <WifiOff size={13} className="inline ml-1.5 text-red-500" />}
            </span>
          </div>
        </div>
        {done && (
          <Link
            to="/articles"
            className="flex items-center gap-2 text-sm font-medium bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <CheckCircle size={15} />
            View Articles
          </Link>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
        <StatCard label="Attempted"   value={s.attempted} />
        <StatCard label="Saved"       value={s.saved}      accent="text-decision-saved" />
        <StatCard label="Blocked"     value={s.blocked}    accent="text-decision-blocked" />
        <StatCard label="Duplicates"  value={s.duplicates} accent="text-amber-600" />
        <StatCard label="Success"     value={`${(s.success_rate * 100).toFixed(0)}%`} accent="text-indigo-600" />
        <StatCard label="Avg Quality" value={s.avg_quality.toFixed(2)} />
      </div>

      <ActivityFeed logs={logs} paused={paused} onPauseToggle={setPaused} bottomRef={bottomRef} />
    </div>
  );
}
