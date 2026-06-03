"""集成冒烟测试 — 全链路 user journey

启动方式:
    # 先启动各服务:
    uvicorn app.main:app --port 8001 &
    cd ../scenic-dh-admin-api && uvicorn app.main:app --port 8002 &
    cd ../scenic-dh-demo-mock-service && uvicorn app.main:app --port 8006 &

    # 然后跑:
    pytest tests/test_integration.py -v

也可单独跑（不依赖外部服务）:
    pytest tests/test_integration.py -v -k "test_"
"""

import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app as business_app
from app.config import settings as business_settings

client = TestClient(business_app)


class TestFullTouristJourney:
    """模拟完整游客旅程：进入 → 浏览 → 提问 → 到达 → 反馈"""

    def test_01_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["code"] == 0

    def test_02_scenic_area_info(self):
        resp = client.get("/v1/scenic-areas/SA-001")
        data = resp.json()["data"]
        assert data["name"] == "灵山胜境"
        assert data["level"] == "5A"
        assert data["source"] == "public_demo_package"

    def test_03_list_all_spots(self):
        resp = client.get("/v1/spots")
        data = resp.json()["data"]
        assert len(data["items"]) >= 16
        # check source marking
        for spot in data["items"]:
            assert "source" in spot, f"spot {spot['id']} missing source"
            assert "freshnessLevel" in spot, f"spot {spot['id']} missing freshnessLevel"

    def test_04_search_spots(self):
        resp = client.get("/v1/spots?keyword=大佛")
        items = resp.json()["data"]["items"]
        assert any("大佛" in s["name"] for s in items)

    def test_05_filter_by_tag(self):
        resp = client.get("/v1/spots?tag=必游")
        items = resp.json()["data"]["items"]
        assert all("必游" in s["tags"] for s in items)

    def test_06_spot_detail_with_guide(self):
        resp = client.get("/v1/spots/LS-002")
        assert resp.json()["data"]["name"] == "灵山梵宫"

        resp = client.get("/v1/spots/LS-002/guide")
        guide = resp.json()["data"]
        assert "briefText" in guide or "shortText" in guide

    def test_07_routes(self):
        resp = client.get("/v1/routes")
        routes = resp.json()["data"]["items"]
        assert len(routes) == 3
        assert routes[0]["source"] == "public_demo_package"

    def test_08_route_plan(self):
        resp = client.post("/v1/routes/plan", json={"interests": ["亲子"], "duration": "4 小时"})
        data = resp.json()["data"]
        assert data["route"]["type"] == "family"

    def test_09_create_session(self):
        resp = client.post("/v1/sessions", json={
            "source": "integration-test",
            "language": "zh",
            "profile": {"language": "zh", "interests": ["佛教文化"], "groupSize": 2, "hasChildren": False},
        })
        data = resp.json()["data"]
        assert data["sessionId"]
        self.session_id = data["sessionId"]

    def test_10_get_session(self):
        self.test_09_create_session()
        resp = client.get(f"/v1/sessions/{self.session_id}")
        session = resp.json()["data"]
        assert session["status"] == "active"
        assert session["profile"]["language"] == "zh"

    def test_11_patch_session(self):
        self.test_09_create_session()
        resp = client.patch(f"/v1/sessions/{self.session_id}", json={"currentSpotId": "LS-001"})
        assert resp.json()["data"]["currentSpotId"] == "LS-001"

    def test_12_post_message(self):
        self.test_09_create_session()
        resp = client.post(f"/v1/sessions/{self.session_id}/messages", json={
            "role": "user",
            "text": "灵山大佛有多高？",
        })
        assert resp.json()["data"]["messageId"]

    def test_13_message_with_citations(self):
        self.test_09_create_session()
        resp = client.post(f"/v1/sessions/{self.session_id}/messages", json={
            "role": "assistant",
            "text": "灵山大佛高88米，加上基座总高达101.5米。",
            "citations": [{"sourceName": "灵山胜境 景点结构化数据集", "chunkId": "LS-001-1", "confidence": 0.95}],
            "confidence": 0.95,
            "fallback": False,
        })
        data = resp.json()
        assert data["code"] == 0

    def test_14_list_messages(self):
        self.test_09_create_session()
        client.post(f"/v1/sessions/{self.session_id}/messages", json={"role": "user", "text": "test"})
        resp = client.get(f"/v1/sessions/{self.session_id}/messages")
        assert len(resp.json()["data"]["messages"]) >= 1

    def test_15_arrival_event(self):
        self.test_09_create_session()
        resp = client.post(f"/v1/sessions/{self.session_id}/arrival-events", json={
            "spotId": "LS-003",
            "location": {"lat": 31.42, "lng": 120.103},
            "trigger": "demo",
        })
        data = resp.json()["data"]
        assert data["accepted"] is True

    def test_16_feedback(self):
        self.test_09_create_session()
        client.post(f"/v1/sessions/{self.session_id}/messages", json={"role": "assistant", "text": "test answer"})
        resp = client.post(f"/v1/sessions/{self.session_id}/feedback", json={
            "rating": 5,
            "resolved": True,
            "comment": "讲解很详细",
        })
        assert resp.json()["data"]["feedbackId"]

    def test_17_full_journey(self):
        """一键跑通完整游客旅程"""
        # Create session
        s = client.post("/v1/sessions", json={"source": "journey-test", "language": "zh"})
        sid = s.json()["data"]["sessionId"]

        # Get spots
        spots = client.get("/v1/spots")
        assert spots.json()["data"]["pagination"]["total"] >= 16

        # Get spot detail
        spot = client.get("/v1/spots/LS-001")
        assert spot.json()["data"]["name"] == "灵山大佛"

        # Get guide
        guide = client.get("/v1/spots/LS-001/guide")
        assert guide.json()["code"] == 0

        # Get routes
        routes = client.get("/v1/routes")
        assert len(routes.json()["data"]["items"]) == 3

        # Update session
        client.patch(f"/v1/sessions/{sid}", json={"currentSpotId": "LS-001"})

        # User asks question
        m1 = client.post(f"/v1/sessions/{sid}/messages", json={"role": "user", "text": "灵山大佛有多高？"})
        assert m1.json()["data"]["messageId"]

        # Assistant answers
        client.post(f"/v1/sessions/{sid}/messages", json={
            "role": "assistant",
            "text": "灵山大佛高88米。",
            "citations": [{"sourceName": "结构化数据集", "confidence": 0.95}],
            "confidence": 0.95,
        })

        # Arrival
        client.post(f"/v1/sessions/{sid}/arrival-events", json={"spotId": "LS-001", "trigger": "demo"})

        # Feedback
        fb = client.post(f"/v1/sessions/{sid}/feedback", json={"rating": 5, "resolved": True})
        assert fb.json()["data"]["feedbackId"]

        # Verify trace headers
        assert "x-trace-id" in fb.headers
        assert "x-service" in fb.headers


class TestAdminSmoke:
    """Admin API 冒烟 — 用 business-api 的 TestClient 模拟（同根）"""
    # Admin API 是独立服务，这里只测 business-api 不依赖 admin 的部分

    def test_scenic_info_completeness(self):
        """验证景区辅助信息接口都可用"""
        endpoints = ["/v1/notices", "/v1/events", "/v1/services", "/v1/weather", "/v1/queues", "/v1/tickets/products"]
        for ep in endpoints:
            resp = client.get(ep)
            assert resp.status_code == 200, f"{ep} failed"
            assert resp.json()["code"] == 0, f"{ep} returned error"


class TestSourceMarking:
    """验证所有数据都有 source 和 freshnessLevel 标记"""

    def test_spots_have_source(self):
        resp = client.get("/v1/spots")
        for spot in resp.json()["data"]["items"]:
            assert spot.get("source") in ("public_demo_package", "manual_seed", "mock", "official"), \
                f"spot {spot['id']} has invalid source: {spot.get('source')}"
            assert spot.get("freshnessLevel") in ("high", "medium", "low", "static"), \
                f"spot {spot['id']} has invalid freshnessLevel: {spot.get('freshnessLevel')}"

    def test_routes_have_source(self):
        resp = client.get("/v1/routes")
        for route in resp.json()["data"]["items"]:
            assert route.get("source") == "public_demo_package"

    def test_weather_is_mock(self):
        resp = client.get("/v1/weather")
        assert resp.json()["data"]["source"] == "mock"

    def test_queues_is_mock(self):
        resp = client.get("/v1/queues")
        assert resp.json()["data"]["source"] == "mock"

    def test_tickets_source(self):
        resp = client.get("/v1/tickets/products")
        for ticket in resp.json()["data"]["items"]:
            assert ticket.get("source") == "public_demo_package"
