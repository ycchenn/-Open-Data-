"""把口述的農事內容整理成結構化農事日誌。"""
import re
from datetime import date

from .llm import LLMClient
from .vocabulary import correct_text, extract_entities

ACTIVITY_KEYWORDS = {
    "施肥": ["施肥", "下肥", "追肥", "基肥"],
    "病蟲害防治": ["噴藥", "防治", "打藥", "噴灑"],
    "灌溉": ["灌溉", "澆水", "放水", "噴灌", "滴灌"],
    "除草": ["除草", "割草", "拔草"],
    "播種定植": ["播種", "定植", "種下", "育苗", "插秧"],
    "整枝修剪": ["修剪", "整枝", "剪枝", "疏果", "疏花", "摘心"],
    "套袋": ["套袋"],
    "採收": ["採收", "收成", "採摘", "收割"],
    "整地": ["整地", "翻土", "犁田"],
}

AMOUNT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(公斤|公克|公升|毫升|cc|CC|包|袋|瓶|倍|箱|台斤|斤)")
FIELD_RE = re.compile(r"([東西南北上下前後]?[一二三四五六七八九十\dA-Za-z]+號?(?:田|園|區|溫室|棚))")
AREA_RE = re.compile(r"([一二三四五六七八九十\d.]+)\s*(分地|分|甲|公頃)")
WEATHER_WORDS = ["晴", "陰", "雨", "颱風", "寒流", "高溫", "多雲"]

SYSTEM_PROMPT = """你是台灣農事紀錄助理。請將農民口述內容整理成 JSON，欄位如下：
{
  "date": "YYYY-MM-DD（未提及則用今天）",
  "crop": "作物名稱或 null",
  "field": "田區名稱或 null",
  "area": "面積（含單位）或 null",
  "weather": "天氣或 null",
  "activities": [
    {"type": "施肥|病蟲害防治|灌溉|除草|播種定植|整枝修剪|套袋|採收|整地|其他",
     "description": "簡述",
     "target": "防治對象（病蟲害名稱）或 null",
     "materials": [{"name": "資材名稱", "amount": 數字或 null, "unit": "單位或 null"}]}
  ],
  "harvest": {"amount": 數字或 null, "unit": "單位或 null"} 或 null,
  "notes": "其他備註或 null"
}
只輸出 JSON，不要臆測口述中沒有的資訊。"""


def _parse_rule_based(text: str) -> dict:
    """未設定 OpenAI 時的備援：以關鍵詞與正規表示式抽取。"""
    entities = extract_entities(text)
    sentences = [s for s in re.split(r"[，。,.；;\n]", text) if s.strip()]

    # 每句歸到它提到的作業；沒提到作業的句子（如「用有機肥料20公斤」）歸到前一個作業
    grouped: dict[str, list[str]] = {}
    current = None
    for sentence in sentences:
        sentence = sentence.strip()
        matched = next((t for t, kws in ACTIVITY_KEYWORDS.items() if any(k in sentence for k in kws)), None)
        if matched is None and any(p in sentence for p in entities["pests"]):
            matched = "病蟲害防治"  # 「發現有薊馬」這類描述病蟲害的句子
        current = matched or current
        if current:
            grouped.setdefault(current, []).append(sentence)

    activities = []
    for act_type, related in grouped.items():
        joined = "，".join(related)
        materials = [{"name": f, "amount": None, "unit": None} for f in entities["fertilizers"] if f in joined]
        for amount, unit in AMOUNT_RE.findall(joined):
            if materials and materials[-1]["amount"] is None:
                materials[-1].update(amount=float(amount), unit=unit)
            else:
                materials.append({"name": None, "amount": float(amount), "unit": unit})
        target = next((p for p in entities["pests"] if p in joined), None) if act_type == "病蟲害防治" else None
        activities.append({"type": act_type, "description": joined, "target": target, "materials": materials})

    harvest = None
    if any(a["type"] == "採收" for a in activities):
        m = AMOUNT_RE.search(next(a["description"] for a in activities if a["type"] == "採收"))
        if m:
            harvest = {"amount": float(m.group(1)), "unit": m.group(2)}

    field = FIELD_RE.search(text)
    area = AREA_RE.search(text)
    return {
        "date": date.today().isoformat(),
        "crop": entities["crops"][0] if entities["crops"] else None,
        "field": field.group(1) if field else None,
        "area": "".join(area.groups()) if area else None,
        "weather": next((w for w in WEATHER_WORDS if w in text), None),
        "activities": activities or [{"type": "其他", "description": text, "target": None, "materials": []}],
        "harvest": harvest,
        "notes": None,
    }


def parse_farm_log(raw_text: str, llm: LLMClient) -> dict:
    if not raw_text.strip():
        raise ValueError("農事內容不可為空")

    corrected, changes = correct_text(raw_text.strip())
    parsed = llm.chat_json(SYSTEM_PROMPT, f"今天日期：{date.today().isoformat()}\n農民口述：{corrected}")
    engine = "openai"
    if not parsed:
        parsed = _parse_rule_based(corrected)
        engine = "rule-based"

    return {
        **parsed,
        "raw_text": raw_text,
        "corrected_text": corrected,
        "corrections": changes,
        "engine": engine,
    }
