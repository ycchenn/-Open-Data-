import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATA_DIR = Path(__file__).parent / "data"


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

    AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-1")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
    AWS_TRANSCRIBE_VOCABULARY = os.getenv("AWS_TRANSCRIBE_VOCABULARY", "")
    POLLY_VOICE_ID = os.getenv("POLLY_VOICE_ID", "Zhiyu")

    FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS", "")

    GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY", "")
    GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")

    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]

    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 音檔上限 20MB
