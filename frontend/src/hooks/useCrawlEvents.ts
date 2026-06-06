import { useCallback, useEffect, useRef, useState } from "react";
import type { CrawlEvent, CrawlLogEntry, CrawlStats } from "../api/types";

export function useCrawlEvents(jobId: string | undefined, enabled: boolean) {
  const [logs, setLogs] = useState<CrawlLogEntry[]>([]);
  const [stats, setStats] = useState<CrawlStats | null>(null);
  const [status, setStatus] = useState<"connecting" | "live" | "done" | "error">("connecting");
  const [paused, setPaused] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  const appendLog = useCallback((entry: CrawlLogEntry) => {
    setLogs((prev) => [...prev, entry]);
  }, []);

  useEffect(() => {
    if (!jobId || !enabled || import.meta.env.VITE_USE_MOCK === "true") return;

    let es: EventSource | null = null;
    let closed = false;

    const connect = () => {
      es = new EventSource(`/api/crawls/${jobId}/events`);
      setStatus("connecting");

      es.onmessage = (ev) => {
        if (closed) return;
        try {
          const event = JSON.parse(ev.data) as CrawlEvent;
          if (event.type === "log") {
            appendLog(event.data);
            setStatus("live");
          } else if (event.type === "stats") {
            setStats(event.data);
          } else if (event.type === "done") {
            setStats(event.data.stats);
            setStatus("done");
            es?.close();
          } else if (event.type === "error") {
            setStatus("error");
          }
        } catch {
          /* ignore parse errors */
        }
      };

      es.onerror = () => {
        if (!closed && status !== "done") {
          setStatus("error");
          es?.close();
        }
      };
    };

    connect();
    return () => {
      closed = true;
      es?.close();
    };
  }, [jobId, enabled, appendLog, status]);

  useEffect(() => {
    if (!paused && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [logs, paused]);

  return { logs, stats, status, paused, setPaused, bottomRef };
}
