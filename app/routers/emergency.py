"""应急求助、工单提交与查询、离线包"""

from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Emergency & Work Orders"])

# ── 种子数据 ──
_WORK_ORDERS: dict[str, dict] = {}
_EMERGENCY_TYPES = [
    {"type": "sos", "label": "紧急求助", "priority": "critical", "responseSLA": 300},
    {"type": "medical", "label": "医疗求助", "priority": "critical", "responseSLA": 300},
    {"type": "lost_child", "label": "走失人员", "priority": "high", "responseSLA": 600},
    {"type": "security", "label": "安保事件", "priority": "high", "responseSLA": 600},
    {"type": "facility", "label": "设施故障", "priority": "medium", "responseSLA": 1800},
    {"type": "complaint", "label": "投诉", "priority": "medium", "responseSLA": 3600},
    {"type": "feedback", "label": "建议", "priority": "low", "responseSLA": 86400},
]
_WO_COUNTER = 0

_OFFLINE_PACKAGES = [
    {
        "version": "1.2.0",
        "releaseDate": "2026-06-10",
        "sizeBytes": 5242880,
        "checksum": "sha256:abc123def456",
        "files": 42,
        "mandatory": False,
        "changelog": "更新基础讲解文案、修复地图POI坐标",
        "downloadUrl": "https://cdn.example.com/offline/scenic-v1.2.0.zip",
    }
]

_EMERGENCY_CONTACTS = [
    {"type": "sos", "name": "景区应急指挥中心", "phone": "023-88880110", "availableHours": "全天"},
    {"type": "medical", "name": "景区医务室", "phone": "023-88880120", "availableHours": "08:00-20:00"},
    {"type": "security", "name": "景区安保部", "phone": "023-88880119", "availableHours": "全天"},
    {"type": "service", "name": "游客服务中心", "phone": "023-88880001", "availableHours": "08:00-18:00"},
]


# ═══ 应急求助 ═══

class EmergencyRequest(BaseModel):
    type: str
    sessionId: str
    lat: float | None = None
    lng: float | None = None
    description: str | None = None
    contactPhone: str | None = None


@router.post("/emergency/requests")
def create_emergency(body: EmergencyRequest, request: Request):
    global _WO_COUNTER
    trace_id = request.state.trace_id

    # 验证类型
    valid_types = {e["type"] for e in _EMERGENCY_TYPES}
    if body.type not in valid_types:
        return err(40001, f"未知应急类型: {body.type}，有效类型: {','.join(valid_types)}", trace_id)

    emergency_type = next(e for e in _EMERGENCY_TYPES if e["type"] == body.type)
    _WO_COUNTER += 1
    wo_id = f"WO-{_WO_COUNTER:04d}"

    wo = {
        "id": wo_id,
        "type": body.type,
        "label": emergency_type["label"],
        "priority": emergency_type["priority"],
        "sessionId": body.sessionId,
        "lat": body.lat,
        "lng": body.lng,
        "description": body.description or "",
        "contactPhone": body.contactPhone or "",
        "status": "pending",
        "assignedTo": None,
        "responseSLA": emergency_type["responseSLA"],
        "resolvedAt": None,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _WORK_ORDERS[wo_id] = wo

    # 匹配应急联系人
    contact = next((c for c in _EMERGENCY_CONTACTS if c["type"] == body.type), _EMERGENCY_CONTACTS[0])

    return ok({
        "workOrderId": wo_id,
        "status": "pending",
        "estimatedResponse": f"{emergency_type['responseSLA'] // 60} 分钟内",
        "emergencyContact": contact,
    }, trace_id)


# ═══ 工单（反馈/投诉） ═══

class CreateWorkOrderRequest(BaseModel):
    type: str
    sessionId: str
    title: str
    description: str | None = None
    category: str = "general"
    lat: float | None = None
    lng: float | None = None
    images: list[str] | None = None
    contactPhone: str | None = None


@router.post("/work-orders")
def create_work_order(body: CreateWorkOrderRequest, request: Request):
    global _WO_COUNTER
    trace_id = request.state.trace_id
    _WO_COUNTER += 1
    wo_id = f"WO-{_WO_COUNTER:04d}"

    wo = {
        "id": wo_id,
        "type": body.type,
        "title": body.title,
        "category": body.category,
        "sessionId": body.sessionId,
        "description": body.description or "",
        "lat": body.lat,
        "lng": body.lng,
        "images": body.images or [],
        "contactPhone": body.contactPhone or "",
        "status": "pending",
        "assignedTo": None,
        "resolution": None,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _WORK_ORDERS[wo_id] = wo
    return ok({"workOrderId": wo_id, "status": "pending"}, trace_id)


@router.get("/work-orders")
def get_work_orders(request: Request, session_id: str | None = None, status: str | None = None):
    trace_id = request.state.trace_id
    orders = list(_WORK_ORDERS.values())
    if session_id:
        orders = [o for o in orders if o["sessionId"] == session_id]
    if status:
        orders = [o for o in orders if o["status"] == status]
    orders.sort(key=lambda o: o["createdAt"], reverse=True)
    return ok({"items": orders, "total": len(orders)}, trace_id)


# ═══ 离线包 ═══

@router.get("/offline-packages/latest")
def get_latest_offline_package(request: Request):
    trace_id = request.state.trace_id
    if not _OFFLINE_PACKAGES:
        return ok({"available": False}, trace_id)
    latest = _OFFLINE_PACKAGES[0]
    latest["available"] = True
    return ok(latest, trace_id)
