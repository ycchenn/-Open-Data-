"""由農事日誌產生產銷履歷生產紀錄草稿。

欄位參考產銷履歷「生產紀錄」常見分類（栽培管理、肥料使用、病蟲害防治、採收），
實際申報仍須依各驗證機構提供之表單格式填寫。
"""

SECTION_BY_ACTIVITY = {
    "施肥": "肥料使用紀錄",
    "病蟲害防治": "病蟲害防治紀錄",
    "採收": "採收紀錄",
}
DEFAULT_SECTION = "栽培管理紀錄"

REQUIRED_FIELDS = {
    "肥料使用紀錄": ["資材名稱", "使用量"],
    "病蟲害防治紀錄": ["防治對象", "資材名稱", "稀釋倍數或使用量"],
    "採收紀錄": ["採收量"],
    "栽培管理紀錄": [],
}

DISCLAIMER = "本草稿由系統自動產生，僅供整理參考；送出前請核對內容，並依驗證機構表單格式填寫。"


def _material_text(materials: list[dict]) -> tuple[str | None, str | None]:
    names = [m["name"] for m in materials if m.get("name")]
    amounts = [f'{m["amount"]:g}{m["unit"] or ""}' for m in materials if m.get("amount") is not None]
    return ("、".join(names) or None, "、".join(amounts) or None)


def build_traceability_draft(log: dict) -> dict:
    base = {"日期": log.get("date"), "作物": log.get("crop"), "田區": log.get("field")}
    sections: dict[str, list[dict]] = {}
    missing: list[str] = []

    for key in ("作物", "田區"):
        if not base[key]:
            missing.append(f"基本資料：{key}")

    for act in log.get("activities", []):
        section = SECTION_BY_ACTIVITY.get(act["type"], DEFAULT_SECTION)
        names, amounts = _material_text(act.get("materials", []))
        row = {**base, "作業項目": act["type"], "作業內容": act.get("description")}

        if section == "肥料使用紀錄":
            row.update({"資材名稱": names, "使用量": amounts})
        elif section == "病蟲害防治紀錄":
            row.update({
                "防治對象": act.get("target"),
                "資材名稱": names,
                "稀釋倍數或使用量": amounts,
                "安全採收期": "請依農藥標示填寫",
            })
        elif section == "採收紀錄":
            harvest = log.get("harvest") or {}
            amount = harvest.get("amount")
            row["採收量"] = f'{amount:g}{harvest.get("unit") or ""}' if amount is not None else None

        for field in REQUIRED_FIELDS[section]:
            if not row.get(field):
                missing.append(f"{section}：{field}")
        sections.setdefault(section, []).append(row)

    return {"sections": sections, "missing_fields": missing, "disclaimer": DISCLAIMER}
