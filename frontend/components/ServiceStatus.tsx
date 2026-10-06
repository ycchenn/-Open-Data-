"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { HealthStatus } from "@/lib/types";

const LABELS: Record<string, string> = {
  openai: "OpenAI（AI 整理／文案）",
  transcribe: "AWS Transcribe（語音轉文字）",
  polly: "AWS Polly（語音播報）",
  search_agent: "官方資料搜尋",
};

export default function ServiceStatus() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [offline, setOffline] = useState(false);

  useEffect(() => {
    api.health().then(setHealth).catch(() => setOffline(true));
  }, []);

  if (offline) return <div className="warning">無法連線到後端服務，請確認 Flask 已啟動。</div>;
  if (!health) return <div className="muted">檢查服務狀態中…</div>;

  return (
    <div className="row">
      {Object.entries(LABELS).map(([key, label]) => (
        <span key={key} className="tag" title={health.services[key] ? "已啟用" : "未設定，使用離線備援"}>
          {health.services[key] ? "✅" : "⚪"} {label}
        </span>
      ))}
      <span className="tag">📚 知識庫段落：{health.services.rag_chunks}</span>
    </div>
  );
}
