"""以行銷 4P（Product / Price / Place / Promotion）架構，從農事紀錄產生品牌故事與行銷文案。"""
from .llm import LLMClient

SYSTEM_PROMPT = """你是台灣在地農產品牌文案顧問，熟悉行銷 4P 理論。
請依據農民提供的真實農事紀錄與產品資訊撰寫文案，規則：
1. 只使用提供的事實，不可誇大療效或捏造認證、得獎紀錄。
2. 語氣溫暖、在地、有人情味，使用繁體中文。
請輸出 JSON：
{
  "four_p": {"product": "...", "price": "...", "place": "...", "promotion": "..."},
  "brand_story": "200 字內品牌故事",
  "social_post": "社群貼文（含 emoji，150 字內）",
  "product_description": "電商商品描述（100 字內）",
  "hashtags": ["#..."]
}"""


def _log_facts(logs: list[dict]) -> str:
    lines = []
    for log in logs:
        acts = "；".join(a.get("description") or a["type"] for a in log.get("activities", []))
        lines.append(f'- {log.get("date")} {log.get("crop") or ""}：{acts}')
    return "\n".join(lines) or "（無農事紀錄）"


def _template(product: dict, logs: list[dict]) -> dict:
    name = product.get("name") or next((l["crop"] for l in logs if l.get("crop")), "我們的農產品")
    farm = product.get("farm_name") or "我們的小農場"
    origin = product.get("origin") or "台灣"
    channel = product.get("channel") or "產地直送"
    price = product.get("price") or "依當季產量定價"
    care = sorted({a["type"] for l in logs for a in l.get("activities", [])} - {"其他"})
    care_text = "、".join(care) if care else "每一個環節"

    return {
        "four_p": {
            "product": f"{origin}{farm}的{name}，每批都有完整農事紀錄可追溯。",
            "price": price,
            "place": channel,
            "promotion": "分享田間日常與農事紀錄，讓消費者看見產品背後的用心。",
        },
        "brand_story": (
            f"在{origin}的{farm}，我們用心照顧每一株{name}。從{care_text}，"
            f"每天的農事都一筆一筆記錄下來，因為我們相信，好吃的{name}來自看得見的用心。"
        ),
        "social_post": f"🌱 今天的{farm}也很努力！{care_text}都沒少做，{name}正在慢慢長大，敬請期待 🧺",
        "product_description": f"{origin}{farm}直送{name}，附產銷紀錄，{channel}，新鮮看得見。",
        "hashtags": [f"#{name}", f"#{origin}", "#在地小農", "#產地直送", "#農情AI語"],
    }


def generate_marketing(product: dict, logs: list[dict], llm: LLMClient) -> dict:
    user = (
        f"產品資訊：{product}\n"
        f"近期農事紀錄：\n{_log_facts(logs)}"
    )
    result = llm.chat_json(SYSTEM_PROMPT, user)
    if result:
        return {**result, "engine": "openai"}
    return {**_template(product, logs), "engine": "template"}
