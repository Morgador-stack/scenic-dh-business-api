"""景区基础信息、公告、活动、服务设施、天气、排队、票务"""

from fastapi import APIRouter, Request

from app.schemas.common import ok, err

router = APIRouter(tags=["Scenic Info"])


@router.get("/scenic-areas/{scenic_id}")
def get_scenic_area(scenic_id: str, request: Request):
    trace_id = request.state.trace_id
    return ok(
        {
            "id": scenic_id,
            "name": "灵山胜境",
            "nameEn": "Lingshan Buddhist Scenic Spot",
            "level": "5A",
            "city": "无锡",
            "intro": "灵山胜境位于无锡太湖国家旅游度假区，是中国著名的佛教文化主题景区...",
            "openTime": "07:00-17:30",
            "rules": ["请勿在佛像前大声喧哗", "保持景区卫生", "禁止无人机未经许可飞行"],
            "source": "public_demo_package",
            "freshnessLevel": "static",
        },
        trace_id,
    )


@router.get("/notices")
def list_notices(type: str = None, active: bool = True, request: Request = None):
    trace_id = request.state.trace_id
    notices = [
        {"id": "NT-001", "type": "info", "title": "梵宫内部修缮通知", "content": "梵宫部分展厅将于6月5日-6月10日进行内部修缮...", "active": True, "expiresAt": "2026-06-10T18:00:00Z"},
        {"id": "NT-002", "type": "alert", "title": "景区入园须知", "content": "五一期间游客较多，建议提前预约门票...", "active": True, "expiresAt": "2026-06-30T18:00:00Z"},
    ]
    return ok({"items": notices}, trace_id)


@router.get("/events")
def list_events(date: str = None, spot_id: str = None, request: Request = None):
    trace_id = request.state.trace_id
    events = [
        {"id": "EV-001", "name": "九龙灌浴表演", "spotId": "LS-003", "time": "每日 10:00, 14:00, 16:00", "description": "大型音乐喷泉表演，再现释迦牟尼诞生场景"},
        {"id": "EV-002", "name": "梵宫祈福法会", "spotId": "LS-002", "time": "每周六 09:30", "description": "梵宫大殿内举行的祈福仪式"},
    ]
    return ok({"items": events}, trace_id)


@router.get("/services")
def list_services(category: str = None, nearby_spot_id: str = None, request: Request = None):
    trace_id = request.state.trace_id
    services = [
        {"id": "SV-001", "category": "toilet", "name": "南门卫生间", "location": "景区南门入口右侧"},
        {"id": "SV-002", "category": "restaurant", "name": "灵山蔬食馆", "location": "大佛广场东侧"},
        {"id": "SV-003", "category": "parking", "name": "P1 停车场", "location": "景区正门外"},
        {"id": "SV-004", "category": "help_point", "name": "游客服务中心", "location": "景区南门入口"},
    ]
    return ok({"items": services}, trace_id)


@router.get("/weather")
def get_weather(scenic_id: str = None, request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        {
            "scenicId": scenic_id or "SA-001",
            "temperature": 26,
            "weather": "多云",
            "warning": None,
            "source": "mock",
        },
        trace_id,
    )


@router.get("/queues")
def get_queues(spot_id: str = None, request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        {
            "spotId": spot_id or "LS-001",
            "queueMinutes": 15,
            "crowdLevel": "medium",
            "source": "mock",
        },
        trace_id,
    )




@router.get("/analytics/visitor-behavior")
def get_visitor_behavior(attraction_name: str = None, date_range: str = None, request: Request = None):
    trace_id = request.state.trace_id
    return ok(
        {
            "totalSamples": 140448,
            "avgSatisfaction": 4.2,
            "avgStayDuration": "3.5h",
            "avgTotalCost": 280,
            "source": "public_demo_package",
        },
        trace_id,
    )
