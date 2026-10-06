import Link from "next/link";
import ServiceStatus from "@/components/ServiceStatus";

const FEATURES = [
  { href: "/record", icon: "🎙️", title: "用說的記農事", desc: "口語說出今天的農事，系統自動轉成文字、校正農業用語，整理成結構化日誌。" },
  { href: "/logs", icon: "📋", title: "產銷履歷草稿", desc: "從農事日誌自動產生產銷履歷生產紀錄草稿，並標出還缺哪些欄位。" },
  { href: "/marketing", icon: "✍️", title: "品牌故事與文案", desc: "以行銷 4P 架構，把真實的農事紀錄轉成品牌故事、社群貼文與商品描述。" },
  { href: "/qa", icon: "💬", title: "農業問答", desc: "查詢政府官方資料回答問題並附上來源；資訊不足或高風險問題會主動提醒。" },
];

export default function Home() {
  return (
    <div className="stack">
      <section className="card">
        <h1 style={{ margin: 0 }}>農情 AI 語</h1>
        <p>把「記錄」和「行銷」串成同一個流程。開口說農事，日誌、產銷履歷、品牌文案一次完成。</p>
        <Link href="/record" className="button">開始記錄 →</Link>
      </section>
      <div className="grid">
        {FEATURES.map((f) => (
          <Link key={f.href} href={f.href} className="card" style={{ textDecoration: "none", color: "inherit" }}>
            <div style={{ fontSize: 36 }}>{f.icon}</div>
            <h3>{f.title}</h3>
            <p className="muted">{f.desc}</p>
          </Link>
        ))}
      </div>
      <section className="card">
        <h3>服務狀態</h3>
        <ServiceStatus />
      </section>
    </div>
  );
}
