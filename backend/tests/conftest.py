import pytest

from app import create_app
from app.config import Config
from app.services.storage import LocalJsonStore


class TestConfig(Config):
    TESTING = True
    OPENAI_API_KEY = ""
    AWS_S3_BUCKET = ""
    FIREBASE_CREDENTIALS = ""
    GOOGLE_CSE_API_KEY = ""


@pytest.fixture
def app(tmp_path):
    app = create_app(TestConfig)
    app.extensions["nongqing"]["store"] = LocalJsonStore(tmp_path / "db.json")
    return app


@pytest.fixture
def client(app):
    return app.test_client()
