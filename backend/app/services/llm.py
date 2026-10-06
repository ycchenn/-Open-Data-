"""OpenAI 包裝層。未設定 API 金鑰時 available 為 False，呼叫端需自行走備援流程。"""
import json
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self, api_key: str, model: str, embedding_model: str):
        self.model = model
        self.embedding_model = embedding_model
        self._client = None
        if api_key:
            from openai import OpenAI

            self._client = OpenAI(api_key=api_key)

    @property
    def available(self) -> bool:
        return self._client is not None

    def chat(self, system: str, user: str, temperature: float = 0.4) -> str | None:
        if not self.available:
            return None
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            return resp.choices[0].message.content
        except Exception:  # noqa: BLE001 — 外部服務失敗一律退回備援
            logger.exception("OpenAI chat 失敗")
            return None

    def chat_json(self, system: str, user: str) -> dict | None:
        if not self.available:
            return None
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            return json.loads(resp.choices[0].message.content)
        except Exception:  # noqa: BLE001
            logger.exception("OpenAI chat_json 失敗")
            return None

    def embed(self, texts: list[str]) -> list[list[float]] | None:
        if not self.available or not texts:
            return None
        try:
            resp = self._client.embeddings.create(model=self.embedding_model, input=texts)
            return [d.embedding for d in resp.data]
        except Exception:  # noqa: BLE001
            logger.exception("OpenAI embedding 失敗")
            return None
