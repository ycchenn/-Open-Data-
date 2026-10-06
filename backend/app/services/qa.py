"""農業問答（RAG）：本地知識庫 → 官方網站搜尋 → LLM 依來源作答；無來源時拒答並提示。"""
from .llm import LLMClient
from .rag.retriever import Retriever
from .rag.search_agent import SearchAgent
from .safety import INSUFFICIENT_INFO, assess_risk

SYSTEM_PROMPT = """你是台灣農業問答助理。只能根據提供的「參考資料」回答，使用繁體中文。
- 每個論點後面以 [1]、[2] 標註引用的資料編號。
- 若參考資料不足以回答，直接回答「資料不足」，不可自行補充。
- 不得提供具體農藥稀釋倍數或混用建議，除非參考資料明確寫出，且須提醒以農藥標示為準。"""


def _format_context(sources: list[dict]) -> str:
    return "\n\n".join(f"[{i}] {s['source']}\n{s['text']}" for i, s in enumerate(sources, start=1))


def answer_question(question: str, llm: LLMClient, retriever: Retriever, agent: SearchAgent) -> dict:
    if not question.strip():
        raise ValueError("問題不可為空")

    risk = assess_risk(question)
    sources = retriever.search(question)
    if len(sources) < 2:
        sources += agent.search(question)

    base = {"risk": risk, "sources": sources}
    if not sources:
        return {**base, "answer": INSUFFICIENT_INFO, "insufficient": True}

    answer = llm.chat(SYSTEM_PROMPT, f"參考資料：\n{_format_context(sources)}\n\n問題：{question}", temperature=0.2)
    if not answer:
        # 無 LLM 時直接列出檢索到的資料摘要
        answer = "以下為查到的官方資料摘要：\n" + "\n".join(
            f"[{i}] {s['text'][:120]}" for i, s in enumerate(sources, start=1)
        )
    insufficient = answer.strip().startswith("資料不足")
    if insufficient:
        answer = INSUFFICIENT_INFO
    return {**base, "answer": answer, "insufficient": insufficient}
