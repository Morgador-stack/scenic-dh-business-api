"""内部接口 — 供编排服务（avatar-orchestrator）调用"""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Internal"])

# 复用已有 seed 数据（从 spots.py 和 routes.py 导入）
from app.routers.spots import _SEED_SPOTS, _SEED_GUIDES
from app.routers.routes import _SEED_ROUTES


class ContextQueryRequest(BaseModel):
    intent: str = ""           # spot_query / route_query / general / arrival
    spot_id: str | None = None
    session_id: str | None = None


@router.post("/internal/v1/context/query")
def context_query(body: ContextQueryRequest, request: Request):
    """结构化上下文查询 — 给编排服务返回聚合后的业务数据

    编排服务（avatar-orchestrator）根据 intent 和 spot_id 请求上下文，
    business-api 聚合相关数据后返回，无需编排层分别调用各接口。
    """
    trace_id = request.state.trace_id

    spot = None
    route = None
    notices = [
        {"id": "NT-001", "type": "info", "title": "九龙灌浴表演时间", "content": "每日 10:00, 14:00, 16:00"},
        {"id": "NT-002", "type": "info", "title": "游览须知", "content": "请保持景区卫生，文明游览"},
    ]
    weather = {"scenicId": "SA-001", "temperature": 26, "weather": "多云", "warning": None, "source": "mock"}

    # 根据 intent 查找相关数据
    if body.spot_id:
        for s in _SEED_SPOTS:
            if s["id"] == body.spot_id:
                spot = s
                # 附带讲解词
                guide = _SEED_GUIDES.get(body.spot_id, {})
                spot = {**spot, "guide": guide}
                break

    if body.intent in ("route_query", "general"):
        route = _SEED_ROUTES[0]  # 默认推荐第一条

    services = [
        {"id": "SV-001", "name": "游客中心", "location": "景区入口", "openTime": "08:00-17:00"},
        {"id": "SV-002", "name": "医务室", "location": "游客中心旁", "openTime": "08:00-20:00"},
    ]

    # 根据 spot 数据估算 confidence
    confidence = 0.85
    if spot and spot.get("guide"):
        confidence = 0.95
    elif body.intent in ("route_query", "general") and route:
        confidence = 0.90

    result = {
        "intent": body.intent,
        "spot": spot,
        "route": route,
        "notices": notices,
        "services": services,
        "weather": weather,
        "confidence": confidence,
        "session_id": body.session_id,
    }

    return ok(result, trace_id)
