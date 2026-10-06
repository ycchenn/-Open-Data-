from app.services.vocabulary import correct_text, extract_entities


def test_correct_common_misrecognition():
    text, changes = correct_text("今天高麗采有碳疽病，下午去噴要")
    assert text == "今天高麗菜有炭疽病，下午去噴藥"
    assert {c["to"] for c in changes} == {"高麗菜", "炭疽病", "噴藥"}


def test_extract_prefers_longer_term():
    entities = extract_entities("小番茄有薊馬")
    assert entities["crops"] == ["小番茄"]
    assert entities["pests"] == ["薊馬"]
