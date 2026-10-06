from flask import Blueprint, jsonify, request

from ..extensions import service
from ..services.marketing import generate_marketing

bp = Blueprint("marketing", __name__)


@bp.post("/marketing/generate")
def generate():
    body = request.get_json(silent=True) or {}
    store = service("store")
    logs = [log for log_id in body.get("log_ids", []) if (log := store.get(log_id))]
    return jsonify(generate_marketing(body.get("product", {}), logs, service("llm")))
