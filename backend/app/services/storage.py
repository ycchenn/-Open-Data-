"""農事日誌儲存：有 Firebase 憑證時用 Firestore，否則寫入本機 JSON 檔。"""
import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from ..config import DATA_DIR

COLLECTION = "farm_logs"


class LogStore(Protocol):
    def add(self, log: dict) -> dict: ...
    def get(self, log_id: str) -> dict | None: ...
    def list(self, limit: int = 50) -> list[dict]: ...
    def delete(self, log_id: str) -> bool: ...


def _stamp(log: dict) -> dict:
    return {**log, "id": uuid.uuid4().hex, "created_at": datetime.now(timezone.utc).isoformat()}


class LocalJsonStore:
    def __init__(self, path: Path = DATA_DIR / "local_db.json"):
        self.path = path
        self._lock = threading.Lock()

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, logs: list[dict]) -> None:
        self.path.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, log: dict) -> dict:
        with self._lock:
            logs = self._read()
            saved = _stamp(log)
            logs.append(saved)
            self._write(logs)
        return saved

    def get(self, log_id: str) -> dict | None:
        return next((l for l in self._read() if l["id"] == log_id), None)

    def list(self, limit: int = 50) -> list[dict]:
        return sorted(self._read(), key=lambda l: l["created_at"], reverse=True)[:limit]

    def delete(self, log_id: str) -> bool:
        with self._lock:
            logs = self._read()
            remaining = [l for l in logs if l["id"] != log_id]
            self._write(remaining)
        return len(remaining) != len(logs)


class FirestoreStore:
    def __init__(self, credentials_path: str):
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            firebase_admin.initialize_app(credentials.Certificate(credentials_path))
        self._col = firestore.client().collection(COLLECTION)

    def add(self, log: dict) -> dict:
        saved = _stamp(log)
        self._col.document(saved["id"]).set(saved)
        return saved

    def get(self, log_id: str) -> dict | None:
        doc = self._col.document(log_id).get()
        return doc.to_dict() if doc.exists else None

    def list(self, limit: int = 50) -> list[dict]:
        query = self._col.order_by("created_at", direction="DESCENDING").limit(limit)
        return [d.to_dict() for d in query.stream()]

    def delete(self, log_id: str) -> bool:
        ref = self._col.document(log_id)
        if not ref.get().exists:
            return False
        ref.delete()
        return True


def create_store(firebase_credentials: str) -> LogStore:
    if firebase_credentials:
        return FirestoreStore(firebase_credentials)
    return LocalJsonStore()
