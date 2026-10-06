from flask import Blueprint, jsonify, request

from ..extensions import service
from ..services.qa import answer_question

bp = Blueprint("qa", __name__)


@bp.post("/qa/ask")
def ask():
    question = (request.get_json(silent=True) or {}).get("question", "")
    return jsonify(answer_question(question, service("llm"), service("retriever"), service("search_agent")))
