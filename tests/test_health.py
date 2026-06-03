"""冒烟测试：health check + core endpoints"""

from fastapi.testclient import TestClient
import pytest
from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert data["data"]["status"] == "ok"
    assert data["data"]["version"] == "1.0.0"


def test_spots_list():
    resp = client.get("/v1/spots")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert len(data["data"]["items"]) > 0
    assert data["data"]["items"][0]["id"].startswith("LS-")


def test_spots_detail():
    resp = client.get("/v1/spots/LS-001")
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["name"] == "灵山大佛"


def test_spots_not_found():
    resp = client.get("/v1/spots/LS-999")
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] != 0
    assert data["code"] == 40401


def test_spot_guide():
    resp = client.get("/v1/spots/LS-001/guide")
    assert resp.status_code == 200
    data = resp.json()
    assert data["data"]["shortText"] == "灵山大佛"
    assert data["data"]["briefText"]


def test_routes_list():
    resp = client.get("/v1/routes")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["data"]["items"]) == 3


def test_create_session():
    resp = client.post("/v1/sessions", json={"source": "test", "language": "zh"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    assert "sessionId" in data["data"]


def test_trace_id_header():
    resp = client.get("/health")
    assert "x-trace-id" in resp.headers
    assert "x-service" in resp.headers
