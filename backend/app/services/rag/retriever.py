"""本地向量檢索。索引檔為 JSONL，每行 {"text", "source", "url", "embedding"}，
由 scripts/build_index.py 從 data/rag/docs/ 產生。索引不存在時檢索結果為空。"""
import json
import math
from pathlib import Path

from ...config import DATA_DIR
from ..llm import LLMClient

INDEX_PATH = DATA_DIR / "rag" / "index.jsonl"
MIN_SCORE = 0.35


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


class Retriever:
    def __init__(self, llm: LLMClient, index_path: Path = INDEX_PATH):
        self.llm = llm
        self.index_path = index_path
        self._chunks: list[dict] | None = None

    @property
    def chunks(self) -> list[dict]:
        if self._chunks is None:
            if self.index_path.exists():
                with self.index_path.open(encoding="utf-8") as f:
                    self._chunks = [json.loads(line) for line in f if line.strip()]
            else:
                self._chunks = []
        return self._chunks

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        if not self.chunks:
            return []
        vectors = self.llm.embed([query])
        if not vectors:
            return []
        scored = [(_cosine(vectors[0], c["embedding"]), c) for c in self.chunks]
        scored.sort(key=lambda s: s[0], reverse=True)
        return [
            {"text": c["text"], "source": c["source"], "url": c.get("url"), "score": round(score, 3)}
            for score, c in scored[:top_k]
            if score >= MIN_SCORE
        ]
