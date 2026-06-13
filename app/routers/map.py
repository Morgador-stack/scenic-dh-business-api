"""地图与POI — 游客端地图页、POI、设施、图层、关闭区域"""

from fastapi import APIRouter, Request, Query

from app.schemas.common import ok

router = APIRouter(tags=["Map"])

# ── 种子数据 ──
_POIS: list[dict] = [
    {"id": "POI-001", "name": "东门入口", "lat": 29.5600, "lng": 106.5500, "type": "entrance", "category": "入口", "floor": 1, "scenicId": "SA-001", "labels": ["主入口", "售票处旁"], "status": "active"},
    {"id": "POI-002", "name": "朝天门广场", "lat": 29.5620, "lng": 106.5520, "type": "scenic_spot", "category": "景点", "floor": 1, "scenicId": "SA-001", "labels": ["热门景点", "拍照点"], "status": "active"},
    {"id": "POI-003", "name": "洪崖洞观景台", "lat": 29.5640, "lng": 106.5540, "type": "scenic_spot", "category": "景点", "floor": 2, "scenicId": "SA-001", "labels": ["夜景", "拍照点"], "status": "active"},
    {"id": "POI-004", "name": "游客中心", "lat": 29.5590, "lng": 106.5490, "type": "service", "category": "服务设施", "floor": 1, "scenicId": "SA-001", "labels": ["咨询", "寄存"], "status": "active"},
    {"id": "POI-005", "name": "医务点", "lat": 29.5610, "lng": 106.5510, "type": "service", "category": "服务设施", "floor": 1, "scenicId": "SA-001", "labels": ["医疗", "急救"], "status": "active"},
    {"id": "POI-006", "name": "西门出口", "lat": 29.5650, "lng": 106.5550, "type": "exit", "category": "出口", "floor": 1, "scenicId": "SA-001", "labels": ["出口"], "status": "active"},
    {"id": "POI-007", "name": "施工区域", "lat": 29.5630, "lng": 106.5530, "type": "closed_area", "category": "关闭区域", "floor": 1, "scenicId": "SA-001", "labels": ["施工中", "禁止通行"], "status": "closed"},
]

_SERVICES: list[dict] = [
    {"id": "SVC-001", "name": "游客中心", "type": "咨询", "lat": 29.5590, "lng": 106.5490, "floor": 1, "hours": "08:00-18:00", "phone": "023-88880001", "scenicId": "SA-001", "status": "active"},
    {"id": "SVC-002", "name": "公共卫生间A", "type": "厕所", "lat": 29.5605, "lng": 106.5505, "floor": 1, "hours": "全天", "scenicId": "SA-001", "status": "active"},
    {"id": "SVC-003", "name": "停车场", "type": "停车", "lat": 29.5580, "lng": 106.5480, "floor": 0, "hours": "06:00-22:00", "scenicId": "SA-001", "status": "active"},
    {"id": "SVC-004", "name": "医务室", "type": "医务", "lat": 29.5610, "lng": 106.5510, "floor": 1, "hours": "08:00-20:00", "phone": "023-88880120", "scenicId": "SA-001", "status": "active"},
    {"id": "SVC-005", "name": "无障碍通道", "type": "无障碍", "lat": 29.5600, "lng": 106.5500, "floor": 1, "scenicId": "SA-001", "status": "active"},
]

_LAYERS: list[dict] = [
    {"id": "layer-poi", "name": "POI 点位", "type": "poi", "visible": True, "zIndex": 10, "data": _POIS},
    {"id": "layer-services", "name": "服务设施", "type": "service", "visible": True, "zIndex": 8, "data": _SERVICES},
    {"id": "layer-routes", "name": "路线", "type": "route", "visible": True, "zIndex": 5, "data": []},
    {"id": "layer-areas", "name": "关闭区域", "type": "area", "visible": True, "zIndex": 15, "data": [p for p in _POIS if p["type"] == "closed_area"]},
]


@router.get("/map/pois")
def get_pois(
    request: Request,
    scenic_id: str = Query("SA-001", description="景区ID"),
    category: str | None = Query(None, description="分类筛选"),
    status: str = Query("active", description="状态：active/closed/all"),
):
    trace_id = request.state.trace_id
    pois = _POIS
    if scenic_id:
        pois = [p for p in pois if p["scenicId"] == scenic_id]
    if category:
        pois = [p for p in pois if p["category"] == category]
    if status != "all":
        pois = [p for p in pois if p["status"] == status]
    return ok({"items": pois, "total": len(pois)}, trace_id)


@router.get("/map/layers")
def get_layers(
    request: Request,
    scenic_id: str = Query("SA-001"),
    types: str | None = Query(None, description="逗号分隔类型筛选"),
):
    trace_id = request.state.trace_id
    layers = _LAYERS
    if types:
        type_list = [t.strip() for t in types.split(",")]
        layers = [l for l in layers if l["type"] in type_list]
    # 不返回 data 里的 POI（太大），前端按需通过 /map/pois 获取
    result = [{"id": l["id"], "name": l["name"], "type": l["type"], "visible": l["visible"], "zIndex": l["zIndex"]} for l in layers]
    return ok({"items": result, "total": len(result)}, trace_id)
