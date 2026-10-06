import type { FarmLog, HealthStatus, MarketingResult, QAResult, TraceabilityDraft } from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}/api${path}`, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error ?? `請求失敗（${res.status}）`);
  }
  return res.status === 204 ? (undefined as T) : res.json();
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const api = {
  health: () => request<HealthStatus>("/health"),

  transcribe: (audio: Blob) => {
    const form = new FormData();
    form.append("audio", audio, "recording.webm");
    return request<{ text: string; corrected_text: string }>("/speech/transcribe", { method: "POST", body: form });
  },

  synthesize: async (text: string) => {
    const res = await fetch(`${BASE_URL}/api/speech/synthesize`, json({ text }));
    if (!res.ok) throw new Error((await res.json().catch(() => ({}))).error ?? "語音播報失敗");
    return res.blob();
  },

  parseLog: (text: string) => request<FarmLog>("/logs/parse", json({ text })),
  saveLog: (log: FarmLog) => request<FarmLog>("/logs", json(log)),
  listLogs: () => request<FarmLog[]>("/logs"),
  deleteLog: (id: string) => request<void>(`/logs/${id}`, { method: "DELETE" }),

  traceabilityDraft: (logId: string) => request<TraceabilityDraft>("/traceability/draft", json({ log_id: logId })),

  generateMarketing: (product: Record<string, string>, logIds: string[]) =>
    request<MarketingResult>("/marketing/generate", json({ product, log_ids: logIds })),

  ask: (question: string) => request<QAResult>("/qa/ask", json({ question })),
};
