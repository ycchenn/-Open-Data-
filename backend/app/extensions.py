"""集中建立各外部服務的 client，讓 route 透過 current_app.extensions 取得。"""
from flask import Flask, current_app

from .services.llm import LLMClient
from .services.storage import create_store
from .services.speech import SpeechService
from .services.rag.retriever import Retriever
from .services.rag.search_agent import SearchAgent


def init_services(app: Flask) -> None:
    cfg = app.config
    llm = LLMClient(cfg["OPENAI_API_KEY"], cfg["OPENAI_MODEL"], cfg["OPENAI_EMBEDDING_MODEL"])
    app.extensions["nongqing"] = {
        "llm": llm,
        "store": create_store(cfg["FIREBASE_CREDENTIALS"]),
        "speech": SpeechService(
            region=cfg["AWS_REGION"],
            bucket=cfg["AWS_S3_BUCKET"],
            vocabulary=cfg["AWS_TRANSCRIBE_VOCABULARY"],
            voice_id=cfg["POLLY_VOICE_ID"],
        ),
        "retriever": Retriever(llm),
        "search_agent": SearchAgent(cfg["GOOGLE_CSE_API_KEY"], cfg["GOOGLE_CSE_ID"]),
    }


def service(name: str):
    return current_app.extensions["nongqing"][name]
