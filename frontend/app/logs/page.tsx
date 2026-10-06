"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import LogDetail from "@/components/LogDetail";
import TraceabilityView from "@/components/TraceabilityView";
import { api } from "@/lib/api";
import type { FarmLog, TraceabilityDraft } from "@/lib/types";

function LogsList() {
  const highlight = useSearchParams().get("highlight");
  const [logs, setLogs] = useState<FarmLog[] | null>(null);
  const [drafts, setDrafts] = useState<Record<string, TraceabilityDraft>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listLogs().then(setLogs).catch((e) => setError(e.message));
  }, []);

  async function toggleDraft(id: string) {
    if (drafts[id]) {
      setDrafts(({ [id]: _, ...rest }) => rest);
      return;
    }
    try {
      const draft = await api.traceabilityDraft(id);
      setDrafts((d) => ({ ...d, [id]: draft }));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  async function remove(id: string) {
    if (!confirm("確定刪除這筆日誌？")) return;
    await api.deleteLog(id);
    setLogs((l) => l?.filter((log) => log.id !== id) ?? null);
  }

  if (error) return <div className="error">{error}</div>;
  if (!logs) return <div className="muted">載入中…</div>;
  if (logs.length === 0)
    return (
      <div className="card">
        還沒有農事日誌。<Link href="/record">去記錄第一筆 →</Link>
      </div>
    );

  return (
    <div className="stack">
      {logs.map((log) => (
        <section
          key={log.id}
          className="card stack"
          style={log.id === highlight ? { borderColor: "var(--green)", borderWidth: 2 } : undefined}
        >
          <LogDetail log={log} />
          <div className="row">
            <button className="secondary" onClick={() => toggleDraft(log.id!)}>
              {drafts[log.id!] ? "收合產銷履歷草稿" : "產生產銷履歷草稿"}
            </button>
            <Link className="button" href={`/marketing?logs=${log.id}`}>用這筆寫文案</Link>
            <button className="danger" onClick={() => remove(log.id!)}>刪除</button>
          </div>
          {drafts[log.id!] && <TraceabilityView draft={drafts[log.id!]} />}
        </section>
      ))}
    </div>
  );
}

export default function LogsPage() {
  return (
    <div className="stack">
      <h2>農事日誌</h2>
      <Suspense fallback={<div className="muted">載入中…</div>}>
        <LogsList />
      </Suspense>
    </div>
  );
}
