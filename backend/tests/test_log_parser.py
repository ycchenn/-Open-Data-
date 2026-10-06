from app.services.llm import LLMClient
from app.services.log_parser import parse_farm_log
from app.services.traceability import build_traceability_draft

OFFLINE = LLMClient("", "gpt-4o-mini", "text-embedding-3-small")


def test_rule_based_parse():
    log = parse_farm_log("今天天氣晴，在A區文丹園施飛，用有機肥料20公斤，下午採收30台斤", OFFLINE)
    assert log["engine"] == "rule-based"
    assert log["crop"] == "文旦"
    assert log["weather"] == "晴"
    types = {a["type"] for a in log["activities"]}
    assert {"施肥", "採收"} <= types
    fert = next(a for a in log["activities"] if a["type"] == "施肥")
    assert fert["materials"][0] == {"name": "有機肥料", "amount": 20.0, "unit": "公斤"}
    assert log["harvest"] == {"amount": 30.0, "unit": "台斤"}


def test_traceability_reports_missing_fields():
    log = parse_farm_log("番茄有薊馬，早上噴藥", OFFLINE)
    draft = build_traceability_draft(log)
    assert "病蟲害防治紀錄" in draft["sections"]
    assert "病蟲害防治紀錄：資材名稱" in draft["missing_fields"]


def test_pest_sentence_goes_to_pest_control():
    log = parse_farm_log("高麗菜田施肥，用有機肥料20公斤，下午發現有薊馬，明天要噴藥", OFFLINE)
    acts = {a["type"]: a for a in log["activities"]}
    assert acts["施肥"]["target"] is None
    assert acts["病蟲害防治"]["target"] == "薊馬"
