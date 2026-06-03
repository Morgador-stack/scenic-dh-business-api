"""路线与推荐接口"""

from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Routes"])

_SEED_ROUTES = [
    {
        "id": "RT-001",
        "scenicId": "SA-001",
        "name": "历史文化深度游",
        "type": "culture",
        "duration": "约 6 小时",
        "persona": "对佛教文化和历史感兴趣的游客",
        "stops": [
            {"order": 1, "spotId": "LS-006", "spotName": "阿育王柱", "stayDuration": "15 分钟", "description": "了解古印度佛教文化的影响"},
            {"order": 2, "spotId": "LS-005", "spotName": "祥符禅寺", "stayDuration": "40 分钟", "description": "探访千年古寺，聆听钟声"},
            {"order": 3, "spotId": "LS-007", "spotName": "降魔浮雕", "stayDuration": "20 分钟", "description": "欣赏佛陀降魔成道的大型浮雕"},
            {"order": 4, "spotId": "LS-001", "spotName": "灵山大佛", "stayDuration": "90 分钟", "description": "登临大佛基座，抱佛脚祈福"},
            {"order": 5, "spotId": "LS-002", "spotName": "灵山梵宫", "stayDuration": "90 分钟", "description": "参观华藏世界大殿和琉璃艺术"},
            {"order": 6, "spotId": "LS-004", "spotName": "五印坛城", "stayDuration": "60 分钟", "description": "感受藏传佛教文化魅力"},
        ],
        "tips": "建议上午 8:30 入园，先参观历史遗迹再登大佛，中午在灵山蔬食馆用餐。",
        "source": "public_demo_package",
    },
    {
        "id": "RT-002",
        "scenicId": "SA-001",
        "name": "自然风光休闲游",
        "type": "nature",
        "duration": "约 5 小时",
        "persona": "喜欢自然景观和轻松游览的家庭游客",
        "stops": [
            {"order": 1, "spotId": "LS-009", "spotName": "天下第一掌", "stayDuration": "20 分钟", "description": "摸佛手祈福"},
            {"order": 2, "spotId": "LS-008", "spotName": "百子戏弥勒", "stayDuration": "30 分钟", "description": "欣赏百子铜雕，适合亲子互动"},
            {"order": 3, "spotId": "LS-003", "spotName": "九龙灌浴", "stayDuration": "40 分钟", "description": "观看音乐喷泉表演"},
            {"order": 4, "spotId": "LS-001", "spotName": "灵山大佛", "stayDuration": "60 分钟", "description": "远观大佛，漫步广场"},
            {"order": 5, "spotId": "LS-011", "spotName": "香水海", "stayDuration": "30 分钟", "description": "欣赏水景，拍照留念"},
        ],
        "tips": "适合带老人小孩的家庭，节奏轻松。九龙灌浴表演 10:00 场次是必看的。",
        "source": "public_demo_package",
    },
    {
        "id": "RT-003",
        "scenicId": "SA-001",
        "name": "亲子家庭欢乐游",
        "type": "family",
        "duration": "约 4 小时",
        "persona": "带孩子的亲子家庭",
        "stops": [
            {"order": 1, "spotId": "LS-008", "spotName": "百子戏弥勒", "stayDuration": "40 分钟", "description": "孩子最喜欢的雕塑群，互动拍照"},
            {"order": 2, "spotId": "LS-009", "spotName": "天下第一掌", "stayDuration": "20 分钟", "description": "摸摸大佛手，许个小心愿"},
            {"order": 3, "spotId": "LS-003", "spotName": "九龙灌浴", "stayDuration": "40 分钟", "description": "观看震撼的喷泉表演"},
            {"order": 4, "spotId": "LS-015", "spotName": "灵山茶室", "stayDuration": "30 分钟", "description": "休息补给，品尝素斋点心"},
        ],
        "tips": "行程紧凑，适合下午入园。九龙灌浴 14:00 场次最适合亲子观看。",
        "source": "public_demo_package",
    },
]


class RoutePlanRequest(BaseModel):
    startSpotId: str | None = None
    duration: str | None = None
    interests: list[str] | None = None


@router.get("/routes")
def list_routes(duration: str = Query(None), persona: str = Query(None), interest: str = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    routes = _SEED_ROUTES
    if duration:
        routes = [r for r in routes if duration in r["duration"]]
    if persona:
        routes = [r for r in routes if persona in r["persona"]]
    return ok({"items": routes}, trace_id)


@router.get("/routes/{route_id}")
def get_route(route_id: str, request: Request):
    trace_id = request.state.trace_id
    for r in _SEED_ROUTES:
        if r["id"] == route_id:
            return ok(r, trace_id)
    return err(40402, f"路线 {route_id} 不存在", trace_id)


@router.post("/routes/plan")
def plan_route(body: RoutePlanRequest, request: Request):
    trace_id = request.state.trace_id
    # MVP: 简单规则匹配
    route = _SEED_ROUTES[0]
    if body.interests and "亲子" in body.interests:
        route = _SEED_ROUTES[2]
    elif body.duration and "5" in body.duration:
        route = _SEED_ROUTES[1]
    return ok({"route": route, "reason": "根据您的偏好推荐的路线"}, trace_id)
