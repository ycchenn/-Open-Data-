"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { QAResult } from "@/lib/types";

interface Message {
  question: string;
  result?: QAResult;
  error?: string;
}

const SUGGESTIONS = ["高麗菜的小菜蛾要怎麼防治？", "文旦什麼時候施肥比較好？", "噴完農藥多久可以採收？"];

export default function QAPage() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false);

  async function ask(q: string) {
    if (!q.trim()) return;
    setQuestion("");
    setBusy(true);
    const index = messages.length;
    setMessages((m) => [...m, { question: q }]);
    try {
      const result = await api.ask(q);
      setMessages((m) => m.map((msg, i) => (i === index ? { ...msg, result } : msg)));
    } catch (e) {
      const error = e instanceof Error ? e.message : String(e);
      setMessages((m) => m.map((msg, i) => (i === index ? { ...msg, error } : msg)));
    } finally {
      setBusy(false);
    }
  }

  async function speak(text: string) {
    try {
      const audio = new Audio(URL.createObjectURL(await api.synthesize(text)));
      await audio.play();
    } catch (e) {
      alert(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <div className="stack">
      <h2>農業問答</h2>
      <p className="muted">回答只根據政府官方資料並附上來源；查無資料時會直接告訴你，不會亂猜。</p>

      {messages.map((m, i) => (
        <div key={i}>
          <div className="chat-msg user">{m.question}</div>
          <div className="chat-msg bot">
            {m.error && <span className="error">{m.error}</span>}
            {!m.result && !m.error && <span className="muted">查詢中…</span>}
            {m.result && (
              <div className="stack">
                {m.result.risk.warnings.map((w) => (
                  <div key={w} className="warning">⚠️ {w}</div>
                ))}
                <div>{m.result.answer}</div>
                {m.result.sources.length > 0 && (
                  <div className="muted">
                    資料來源：
                    <ol>
                      {m.result.sources.map((s, j) => (
                        <li key={j}>{s.url ? <a href={s.url} target="_blank" rel="noreferrer">{s.source}</a> : s.source}</li>
                      ))}
                    </ol>
                  </div>
                )}
                <div><button className="secondary" onClick={() => speak(m.result!.answer)}>🔊 唸給我聽</button></div>
              </div>
            )}
          </div>
        </div>
      ))}

      <section className="card stack">
        <div className="row">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="secondary" onClick={() => ask(s)} disabled={busy}>{s}</button>
          ))}
        </div>
        <form className="row" onSubmit={(e) => { e.preventDefault(); ask(question); }}>
          <input
            style={{ flex: 1, minWidth: 200 }}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="輸入你的農業問題"
          />
          <button type="submit" disabled={busy || !question.trim()}>送出</button>
        </form>
      </section>
    </div>
  );
}
