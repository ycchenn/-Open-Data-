import type { TraceabilityDraft } from "@/lib/types";

export default function TraceabilityView({ draft }: { draft: TraceabilityDraft }) {
  return (
    <div className="stack">
      {Object.entries(draft.sections).map(([section, rows]) => {
        const columns = Array.from(new Set(rows.flatMap((r) => Object.keys(r))));
        return (
          <div key={section}>
            <h4>{section}</h4>
            <div className="table-wrap">
              <table>
                <thead><tr>{columns.map((c) => <th key={c}>{c}</th>)}</tr></thead>
                <tbody>
                  {rows.map((r, i) => (
                    <tr key={i}>{columns.map((c) => <td key={c}>{r[c] ?? <span className="error">待補</span>}</td>)}</tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      })}
      {draft.missing_fields.length > 0 && (
        <div className="warning">⚠️ 尚缺欄位：{draft.missing_fields.join("、")}</div>
      )}
      <div className="muted">{draft.disclaimer}</div>
    </div>
  );
}
