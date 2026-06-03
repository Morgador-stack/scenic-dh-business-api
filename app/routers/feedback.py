"""反馈接口"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Request, Query
from pydantic import BaseModel

from app.schemas.common import ok

router = APIRouter(tags=["Feedback"])

_FEEDBACKS: list[dict] = []


class FeedbackRequest(BaseModel):
    rating: int
    resolved: bool = True
    comment: str | None = None
    messageId: str | None = None


@router.post("/sessions/{session_id}/feedback")
def create_feedback(session_id: str, body: FeedbackRequest, request: Request):
    trace_id = request.state.trace_id
    feedback_id = str(uuid.uuid4())
    fb = {
        "id": feedback_id,
        "sessionId": session_id,
        "messageId": body.messageId,
        "rating": body.rating,
        "resolved": body.resolved,
        "comment": body.comment,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _FEEDBACKS.append(fb)
    return ok({"feedbackId": feedback_id}, trace_id)


@router.get("/feedback")
def list_feedback(date_range: str = Query(None), rating: int = Query(None), request: Request = None):
    trace_id = request.state.trace_id
    items = _FEEDBACKS
    if rating:
        items = [f for f in items if f["rating"] == rating]
    return ok({"items": items, "total": len(items)}, trace_id)
