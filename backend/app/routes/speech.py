from flask import Blueprint, Response, jsonify, request

from ..extensions import service
from ..services.speech import SpeechNotConfigured
from ..services.vocabulary import correct_text

bp = Blueprint("speech", __name__)

ALLOWED_FORMATS = {"webm", "mp3", "mp4", "wav", "flac", "ogg", "m4a"}


@bp.post("/speech/transcribe")
def transcribe():
    audio = request.files.get("audio")
    if audio is None:
        raise ValueError("請上傳 audio 檔案")
    media_format = (audio.filename or "audio.webm").rsplit(".", 1)[-1].lower()
    if media_format not in ALLOWED_FORMATS:
        raise ValueError(f"不支援的音檔格式：{media_format}")

    try:
        text = service("speech").transcribe(audio.read(), media_format)
    except SpeechNotConfigured as err:
        return jsonify({"error": str(err)}), 503

    corrected, changes = correct_text(text)
    return jsonify({"text": text, "corrected_text": corrected, "corrections": changes})


@bp.post("/speech/synthesize")
def synthesize():
    text = (request.get_json(silent=True) or {}).get("text", "").strip()
    if not text:
        raise ValueError("text 不可為空")
    try:
        audio = service("speech").synthesize(text)
    except SpeechNotConfigured as err:
        return jsonify({"error": str(err)}), 503
    return Response(audio, mimetype="audio/mpeg")
