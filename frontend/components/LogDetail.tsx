import type { FarmLog } from "@/lib/types";

function formatMaterials(log: FarmLog["activities"][number]) {
  return log.materials
    .map((m) => [m.name, m.amount != null ? `${m.amount}${m.unit ?? ""}` : null].filter(Boolean).join(" "))
    .filter(Boolean)
    .join("、");
}

export default function LogDetail({ log }: { log: FarmLog }) {
  return (
    <div className="stack">
      <div className="row">
        <span className="tag">📅 {log.date}</span>
        {log.crop && <span className="tag">🌾 {log.crop}</span>}
        {log.field && <span className="tag">📍 {log.field}</span>}
        {log.area && <span className="tag">📐 {log.area}</span>}
        {log.weather && <span className="tag">⛅ {log.weather}</span>}
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr><th>作業</th><th>內容</th><th>對象</th><th>資材／用量</th></tr>
          </thead>
          <tbody>
            {log.activities.map((a, i) => (
              <tr key={i}>
                <td>{a.type}</td>
                <td>{a.description}</td>
                <td>{a.target ?? "—"}</td>
                <td>{formatMaterials(a) || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {log.corrections?.length > 0 && (
        <div className="muted">
          詞彙校正：{log.corrections.map((c) => `「${c.from}」→「${c.to}」`).join("、")}
        </div>
      )}
    </div>
  );
}
