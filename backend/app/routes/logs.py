from flask import Blueprint, jsonify, request

from ..extensions import service
from ..services.log_parser import parse_farm_log

bp = Blueprint("logs", __name__)


@bp.post("/logs/parse")
def parse():
    text = (request.get_json(silent=True) or {}).get("text", "")
    return jsonify(parse_farm_log(text, service("llm")))


@bp.get("/logs")
def list_logs():
    limit = min(int(request.args.get("limit", 50)), 200)
    return jsonify(service("store").list(limit))


@bp.post("/logs")
def create_log():
    log = request.get_json(silent=True)
    if not isinstance(log, dict) or not log.get("activities"):
        raise ValueError("日誌格式錯誤：缺少 activities")
    log.pop("id", None)
    return jsonify(service("store").add(log)), 201


@bp.get("/logs/<log_id>")
def get_log(log_id: str):
    log = service("store").get(log_id)
    if log is None:
        return jsonify({"error": "找不到此日誌"}), 404
    return jsonify(log)


@bp.delete("/logs/<log_id>")
def delete_log(log_id: str):
    if not service("store").delete(log_id):
        return jsonify({"error": "找不到此日誌"}), 404
    return "", 204
