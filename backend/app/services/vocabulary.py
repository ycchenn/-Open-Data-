"""農業專有詞彙校正：修正語音辨識常見的同音誤字，並抽取作物、病蟲害、肥料等關鍵詞。"""
import json
from functools import lru_cache

from ..config import DATA_DIR


@lru_cache(maxsize=1)
def load_terms() -> dict:
    return json.loads((DATA_DIR / "agri_terms.json").read_text(encoding="utf-8"))


def correct_text(text: str) -> tuple[str, list[dict]]:
    """回傳 (校正後文字, 修改清單)。長詞優先取代，避免短詞先吃掉長詞的一部分。"""
    corrections = load_terms()["corrections"]
    changes = []
    for wrong in sorted(corrections, key=len, reverse=True):
        right = corrections[wrong]
        if wrong != right and wrong in text:
            changes.append({"from": wrong, "to": right, "count": text.count(wrong)})
            text = text.replace(wrong, right)
    return text, changes


def _find_all(text: str, words: list[str]) -> list[str]:
    # 若同時命中「番茄」與「小番茄」，只保留較長者
    hits = [w for w in words if w in text]
    return [w for w in hits if not any(w != o and w in o for o in hits)]


def extract_entities(text: str) -> dict:
    terms = load_terms()
    return {
        "crops": _find_all(text, terms["crops"]),
        "pests": _find_all(text, terms["pests"]),
        "fertilizers": _find_all(text, terms["fertilizers"]),
    }
