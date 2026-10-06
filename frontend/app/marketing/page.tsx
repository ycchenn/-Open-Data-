"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import type { FarmLog, MarketingResult } from "@/lib/types";

const PRODUCT_FIELDS = [
  { key: "name", label: "產品名稱", placeholder: "例：高山高麗菜" },
  { key: "farm_name", label: "農場名稱", placeholder: "例：阿明的菜園" },
  { key: "origin", label: "產地", placeholder: "例：南投仁愛" },
  { key: "price", label: "價格（Price）", placeholder: "例：一顆 80 元，滿 5 顆免運" },
  { key: "channel", label: "通路（Place）", placeholder: "例：產地直送、農夫市集" },
];

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      className="secondary"
      onClick={() => navigator.clipboard.writeText(text).then(() => setCopied(true))}
    >
      {copied ? "已複製" : "複製"}
    </button>
  );
}

function MarketingForm() {
  const initialIds = useSearchParams().get("logs")?.split(",").filter(Boolean) ?? [];
  const [logs, setLogs] = useState<FarmLog[]>([]);
  const [selected, setSelected] = useState<string[]>(initialIds);
  const [product, setProduct] = useState<Record<string, string>>({});
  const [result, setResult] = useState<MarketingResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listLogs().then(setLogs).catch((e) => setError(e.message));
  }, []);

  function toggle(id: string) {
    setSelected((s) => (s.includes(id) ? s.filter((x) => x !== id) : [...s, id]));
  }

  async function generate() {
    setBusy(true);
    setError(null);
    try {
      setResult(await api.generateMarketing(product, selected));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  const outputs = result && [
    { title: "品牌故事", text: result.brand_story },
    { title: "社群貼文", text: `${result.social_post}\n\n${result.hashtags.join(" ")}` },
    { title: "商品描述", text: result.product_description },
  ];

  return (
    <div className="stack">
      <section className="card stack">
        <h3>產品資訊</h3>
        <div className="grid">
          {PRODUCT_FIELDS.map((f) => (
            <div key={f.key}>
              <label htmlFor={f.key}>{f.label}</label>
              <input
                id={f.key}
                placeholder={f.placeholder}
                value={product[f.key] ?? ""}
                onChange={(e) => setProduct((p) => ({ ...p, [f.key]: e.target.value }))}
              />
            </div>
          ))}
        </div>
        <h3>引用的農事紀錄</h3>
        {logs.length === 0 && <div className="muted">尚無日誌，文案將只依產品資訊產生。</div>}
        {logs.map((log) => (
          <label key={log.id} style={{ fontWeight: 400 }}>
            <input
              type="checkbox"
              style={{ width: "auto", marginRight: 8 }}
              checked={selected.includes(log.id!)}
              onChange={() => toggle(log.id!)}
            />
            {log.date} {log.crop ?? ""} — {log.activities.map((a) => a.type).join("、")}
          </label>
        ))}
        <div className="row">
          <button onClick={generate} disabled={busy}>{busy ? "產生中…" : "產生文案"}</button>
        </div>
        {error && <div className="error">{error}</div>}
      </section>

      {result && (
        <>
          <section className="card">
            <h3>行銷 4P 分析</h3>
            <table>
              <tbody>
                <tr><th>產品 Product</th><td>{result.four_p.product}</td></tr>
                <tr><th>價格 Price</th><td>{result.four_p.price}</td></tr>
                <tr><th>通路 Place</th><td>{result.four_p.place}</td></tr>
                <tr><th>推廣 Promotion</th><td>{result.four_p.promotion}</td></tr>
              </tbody>
            </table>
          </section>
          {outputs!.map((o) => (
            <section key={o.title} className="card stack">
              <div className="row" style={{ justifyContent: "space-between" }}>
                <h3 style={{ margin: 0 }}>{o.title}</h3>
                <CopyButton text={o.text} />
              </div>
              <div style={{ whiteSpace: "pre-wrap" }}>{o.text}</div>
            </section>
          ))}
          <div className="muted">產生方式：{result.engine === "openai" ? "AI 生成" : "範本（未設定 OpenAI）"}</div>
        </>
      )}
    </div>
  );
}

export default function MarketingPage() {
  return (
    <div className="stack">
      <h2>品牌故事與行銷文案</h2>
      <Suspense fallback={<div className="muted">載入中…</div>}>
        <MarketingForm />
      </Suspense>
    </div>
  );
}
