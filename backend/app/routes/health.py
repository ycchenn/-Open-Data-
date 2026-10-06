from flask import Blueprint, jsonify

from ..extensions import service

bp = Blueprint("health", __name__)


@bp.get("/health")
def health():
    speech = service("speech")
    return jsonify({
        "status": "ok",
        "services": {
            "openai": service("llm").available,
            "transcribe": speech.transcribe_available,
            "polly": speech.tts_available,
            "search_agent": service("search_agent").available,
            "rag_chunks": len(service("retriever").chunks),
            "storage": type(service("store")).__name__,
        },
    })
