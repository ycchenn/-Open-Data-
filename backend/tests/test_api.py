def test_health(client):
    body = client.get("/api/health").get_json()
    assert body["status"] == "ok"
    assert body["services"]["openai"] is False


def test_log_roundtrip(client):
    parsed = client.post("/api/logs/parse", json={"text": "高麗菜田澆水"}).get_json()
    saved = client.post("/api/logs", json=parsed)
    assert saved.status_code == 201
    log_id = saved.get_json()["id"]
    assert client.get(f"/api/logs/{log_id}").get_json()["crop"] == "高麗菜"

    draft = client.post("/api/traceability/draft", json={"log_id": log_id}).get_json()
    assert "栽培管理紀錄" in draft["sections"]

    marketing = client.post("/api/marketing/generate", json={"log_ids": [log_id]}).get_json()
    assert marketing["engine"] == "template"
    assert "高麗菜" in marketing["brand_story"]

    assert client.delete(f"/api/logs/{log_id}").status_code == 204


def test_qa_without_sources_is_insufficient_and_flags_risk(client):
    body = client.post("/api/qa/ask", json={"question": "這個農藥要稀釋幾倍？"}).get_json()
    assert body["insufficient"] is True
    assert body["risk"]["level"] == "high"


def test_transcribe_without_aws_returns_503(client):
    import io

    resp = client.post(
        "/api/speech/transcribe",
        data={"audio": (io.BytesIO(b"fake"), "a.webm")},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 503
