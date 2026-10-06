"""建立 RAG 向量索引。

把官方資料（.txt / .md）放到 app/data/rag/docs/，第一行可寫 `url: https://...` 標註來源，
執行：python -m scripts.build_index
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import DATA_DIR, Config  # noqa: E402
from app.services.llm import LLMClient  # noqa: E402
from app.services.rag.retriever import INDEX_PATH  # noqa: E402

DOCS_DIR = DATA_DIR / "rag" / "docs"
CHUNK_SIZE = 400
CHUNK_OVERLAP = 80
BATCH_SIZE = 64


def chunk(text: str) -> list[str]:
    step = CHUNK_SIZE - CHUNK_OVERLAP
    return [text[i : i + CHUNK_SIZE] for i in range(0, max(len(text) - CHUNK_OVERLAP, 1), step)]


def load_docs() -> list[dict]:
    chunks = []
    for path in sorted(DOCS_DIR.glob("**/*")):
        if path.suffix not in {".txt", ".md"}:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        url = None
        if lines and lines[0].startswith("url:"):
            url = lines.pop(0).removeprefix("url:").strip()
        for piece in chunk("\n".join(lines).strip()):
            chunks.append({"text": piece, "source": path.stem, "url": url})
    return chunks


def main() -> None:
    llm = LLMClient(Config.OPENAI_API_KEY, Config.OPENAI_MODEL, Config.OPENAI_EMBEDDING_MODEL)
    if not llm.available:
        sys.exit("需要設定 OPENAI_API_KEY 才能建立向量索引")

    chunks = load_docs()
    if not chunks:
        sys.exit(f"{DOCS_DIR} 中沒有可索引的文件")

    with INDEX_PATH.open("w", encoding="utf-8") as f:
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i : i + BATCH_SIZE]
            vectors = llm.embed([c["text"] for c in batch])
            if vectors is None:
                sys.exit("Embedding 失敗，請檢查 API 金鑰")
            for c, v in zip(batch, vectors):
                f.write(json.dumps({**c, "embedding": v}, ensure_ascii=False) + "\n")
    print(f"已寫入 {len(chunks)} 個段落至 {INDEX_PATH}")


if __name__ == "__main__":
    main()
