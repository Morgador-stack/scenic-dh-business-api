"""排队与预约 — 取号、查看、取消；演出/点位预约"""

from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Queues & Reservations"])

# ── 种子数据 ──
_QUEUE_COUNTERS: dict[str, int] = {"QP-001": 15, "QP-002": 8}
_QUEUE_TICKETS: dict[str, dict] = {}
_RESERVATIONS: dict[str, dict] = {}

_RESOURCES: list[dict] = [
    {"id": "QP-001", "name": "洪崖洞观景台", "type": "spot", "capacity": 50, "currentWait": 20, "currentQueue": 15, "status": "open"},
    {"id": "QP-002", "name": "夜景灯光秀", "type": "event", "capacity": 200, "currentWait": 10, "currentQueue": 8, "status": "open"},
    {"id": "QP-003", "name": "朝天门广场演出", "type": "event", "capacity": 100, "currentWait": 0, "currentQueue": 0, "status": "paused"},
]


class CreateQueueTicketRequest(BaseModel):
    resourceId: str
    sessionId: str
    phone: str | None = None
    partySize: int = 1


class CreateReservationRequest(BaseModel):
    resourceId: str
    sessionId: str
    date: str
    slot: str
    partySize: int = 1
    phone: str | None = None


@router.get("/queues")
def _list_queues_disabled(request: Request, scenic_id: str = "SA-001", type: str | None = None):
    trace_id = request.state.trace_id
    resources = _RESOURCES
    if type:
        resources = [r for r in resources if r["type"] == type]
    return ok({"items": resources, "total": len(resources)}, trace_id)


@router.post("/queue/tickets")
def create_queue_ticket(body: CreateQueueTicketRequest, request: Request):
    trace_id = request.state.trace_id
    resource = next((r for r in _RESOURCES if r["id"] == body.resourceId), None)
    if not resource:
        return err(40404, f"资源 {body.resourceId} 不存在", trace_id)
    if resource["status"] != "open":
        return err(40001, f"资源 {resource['name']} 暂不接受排队", trace_id)

    ticket_no = _QUEUE_COUNTERS.get(body.resourceId, 0) + 1
    _QUEUE_COUNTERS[body.resourceId] = ticket_no
    ticket_id = f"QT-{body.resourceId}-{ticket_no}"

    ticket = {
        "id": ticket_id,
        "resourceId": body.resourceId,
        "resourceName": resource["name"],
        "sessionId": body.sessionId,
        "queueNumber": ticket_no,
        "partySize": body.partySize,
        "status": "waiting",
        "estimatedWaitMinutes": resource["currentWait"] + body.partySize * 5,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _QUEUE_TICKETS[ticket_id] = ticket
    resource["currentQueue"] += 1
    return ok(ticket, trace_id)


@router.post("/reservations")
def create_reservation(body: CreateReservationRequest, request: Request):
    trace_id = request.state.trace_id
    resource = next((r for r in _RESOURCES if r["id"] == body.resourceId), None)
    if not resource:
        return err(40404, f"资源 {body.resourceId} 不存在", trace_id)
    if resource["status"] not in ("open", "paused"):
        return err(40001, f"资源 {resource['name']} 暂不接受预约", trace_id)

    reservation_id = f"RES-{body.resourceId}-{body.date}-{body.slot}-{body.partySize}"
    reservation = {
        "id": reservation_id,
        "resourceId": body.resourceId,
        "resourceName": resource["name"],
        "sessionId": body.sessionId,
        "date": body.date,
        "slot": body.slot,
        "partySize": body.partySize,
        "status": "confirmed",
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _RESERVATIONS[reservation_id] = reservation
    return ok(reservation, trace_id)
