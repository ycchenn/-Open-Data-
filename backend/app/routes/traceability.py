from flask import Blueprint, jsonify, request

from ..extensions import service
from ..services.traceability import build_traceability_draft

bp = Blueprint("traceability", __name__)


@bp.post("/traceability/draft")
def draft():
    body = request.get_json(silent=True) or {}
    log = service("store").get(body["log_id"]) if body.get("log_id") else body.get("log")
    if not log:
        raise ValueError("請提供 log_id 或 log")
    return jsonify(build_traceability_draft(log))
