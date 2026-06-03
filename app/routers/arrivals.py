"""到达事件接口"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok

router = APIRouter(tags=["Arrivals"])

_ARRIVALS: dict[str, list[dict]] = {}


class ArrivalEventRequest(BaseModel):
    spotId: str
    location: dict | None = None
    trigger: str = "manual"


@router.post("/sessions/{session_id}/arrival-events")
def create_arrival(session_id: str, body: ArrivalEventRequest, request: Request):
    trace_id = request.state.trace_id
    event_id = str(uuid.uuid4())
    event = {
        "id": event_id,
        "sessionId": session_id,
        "spotId": body.spotId,
        "location": body.location or {"lat": 31.42, "lng": 120.10},
        "trigger": body.trigger,
        "accepted": True,  # MVP 阶段直接接受
        "speechState": "queued",
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _ARRIVALS.setdefault(session_id, []).append(event)
    return ok({"eventId": event_id, "accepted": True}, trace_id)


@router.get("/sessions/{session_id}/arrival-events")
def list_arrivals(session_id: str, request: Request):
    trace_id = request.state.trace_id
    events = _ARRIVALS.get(session_id, [])
    return ok({"events": events}, trace_id)
