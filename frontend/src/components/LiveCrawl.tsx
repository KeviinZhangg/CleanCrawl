import { Link } from "react-router-dom";
import { CheckCircle, Wifi, WifiOff } from "lucide-react";
import { useCrawlJob } from "../api/client";
import { useCrawlEvents } from "../hooks/useCrawlEvents";
import { ActivityFeed } from "./ActivityFeed";
import { StatCard } from "./StatCard";
import { PageHeader } from "./PageHeader";
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
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <PageHeader
          label={isLive ? "Live crawl" : done ? "Crawl complete" : "Crawl"}
          title={`Job #${jobId}`}
          subtitle={`${job?.status ?? status}${isLive ? " — decisions streaming in real time" : ""}`}
        />
        <div className="flex items-center gap-2 pt-8 shrink-0">
          {isLive && <Wifi size={14} className="text-decision-saved" />}
          {isError && <WifiOff size={14} className="text-decision-blocked" />}
          {done && (
            <Link to="/articles" className="mesh-btn-primary !text-xs !px-4 !py-2">
              <CheckCircle size={14} />
              View Articles
            </Link>
          )}
        </div>
      </div>

      <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
        <StatCard label="Attempted"   value={s.attempted} />
        <StatCard label="Saved"       value={s.saved}      accent="text-decision-saved" />
        <StatCard label="Blocked"     value={s.blocked}    accent="text-decision-blocked" />
        <StatCard label="Duplicates"  value={s.duplicates} accent="text-decision-duplicate" />
        <StatCard label="Success"     value={`${(s.success_rate * 100).toFixed(0)}%`} accent="text-mesh-accent" />
        <StatCard label="Avg Quality" value={s.avg_quality.toFixed(2)} />
      </div>

      <ActivityFeed logs={logs} paused={paused} onPauseToggle={setPaused} bottomRef={bottomRef} />
    </div>
  );
}
