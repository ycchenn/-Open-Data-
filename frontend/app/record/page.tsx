"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import LogDetail from "@/components/LogDetail";
import VoiceRecorder from "@/components/VoiceRecorder";
import { api } from "@/lib/api";
import type { FarmLog } from "@/lib/types";

const EXAMPLE = "今天天氣晴，在A區高麗菜田施肥，用有機肥料20公斤，下午發現有薊馬，明天要噴藥。";

export default function RecordPage() {
  const router = useRouter();
  const [text, setText] = useState("");
  const [log, setLog] = useState<FarmLog | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function run<T>(label: string, task: () => Promise<T>) {
    setBusy(label);
    setError(null);
    try {
      return await task();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  }

  async function handleRecorded(audio: Blob) {
    const result = await run("語音辨識中…", () => api.transcribe(audio));
    if (result) setText(result.corrected_text);
  }

  async function handleParse() {
    const result = await run("整理農事日誌中…", () => api.parseLog(text));
    if (result) setLog(result);
  }

  async function handleSave() {
    if (!log) return;
    const saved = await run("儲存中…", () => api.saveLog(log));
    if (saved) router.push(`/logs?highlight=${saved.id}`);
  }

  return (
    <div className="stack">
      <section className="card stack">
        <h2>說說今天的農事</h2>
        <VoiceRecorder onRecorded={handleRecorded} disabled={!!busy} />
        <label htmlFor="log-text">農事內容（可直接編輯或打字）</label>
        <textarea id="log-text" value={text} onChange={(e) => setText(e.target.value)} placeholder={EXAMPLE} />
        <div className="row">
          <button onClick={handleParse} disabled={!text.trim() || !!busy}>整理成日誌</button>
          <button className="secondary" onClick={() => setText(EXAMPLE)} disabled={!!busy}>填入範例</button>
          {busy && <span className="muted">{busy}</span>}
        </div>
        {error && <div className="error">{error}</div>}
      </section>

      {log && (
        <section className="card stack">
          <h3>農事日誌預覽 <span className="muted">（{log.engine === "openai" ? "AI 整理" : "規則式整理"}）</span></h3>
          <LogDetail log={log} />
          <button onClick={handleSave} disabled={!!busy}>儲存日誌</button>
        </section>
      )}
    </div>
  );
}
