"""農業問答的風險分級。高風險問題（用藥劑量、混藥、人體健康）即使有資料也必須附加警示。"""

HIGH_RISK_PATTERNS = {
    "pesticide_dosage": ["稀釋", "倍數", "劑量", "用量", "濃度", "幾cc", "幾毫升"],
    "pesticide_mixing": ["混用", "混合", "一起噴", "加在一起"],
    "human_health": ["中毒", "誤食", "吸入", "皮膚", "頭暈", "嘔吐", "孕婦", "小孩"],
    "banned_substance": ["禁用", "巴拉刈", "加保扶", "違規"],
    "harvest_interval": ["安全採收期", "多久可以採", "噴完多久"],
}

WARNINGS = {
    "pesticide_dosage": "農藥使用量請以農藥標示及「農藥資訊服務網」公告為準，勿依本系統回答自行調整。",
    "pesticide_mixing": "農藥混用可能產生藥害或毒性變化，請先諮詢各區農業改良場或植物醫師。",
    "human_health": "若有疑似中毒症狀，請立即就醫或撥打毒藥物諮詢專線（台北榮總 02-2875-7525）。",
    "banned_substance": "涉及禁用或管制農藥，請依農業部最新公告辦理。",
    "harvest_interval": "安全採收期依藥劑與作物而異，請以農藥標示為準，以免農藥殘留超標。",
}

INSUFFICIENT_INFO = "查無足夠的官方資料可回答此問題，建議洽詢當地農會、農業改良場或植物醫師。"


def assess_risk(question: str) -> dict:
    categories = [cat for cat, words in HIGH_RISK_PATTERNS.items() if any(w in question for w in words)]
    return {
        "level": "high" if categories else "normal",
        "categories": categories,
        "warnings": [WARNINGS[c] for c in categories],
    }
