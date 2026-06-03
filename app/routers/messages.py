"""消息记录接口"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Messages"])

_MESSAGES: dict[str, list[dict]] = {}


class CreateMessageRequest(BaseModel):
    role: str = "user"
    text: str
    citations: list[dict] | None = None
    fallback: bool = False
    fallbackReason: str | None = None
    confidence: float | None = None
    speechState: str | None = None
    durationMs: int | None = None


@router.post("/sessions/{session_id}/messages")
def create_message(session_id: str, body: CreateMessageRequest, request: Request):
    trace_id = request.state.trace_id
    message_id = str(uuid.uuid4())
    msg = {
        "id": message_id,
        "sessionId": session_id,
        "role": body.role,
        "text": body.text,
        "citations": body.citations or [],
        "fallback": body.fallback,
        "fallbackReason": body.fallbackReason,
        "confidence": body.confidence,
        "speechState": body.speechState or "done",
        "durationMs": body.durationMs,
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    _MESSAGES.setdefault(session_id, []).append(msg)
    return ok({"messageId": message_id}, trace_id)


@router.get("/sessions/{session_id}/messages")
def list_messages(session_id: str, limit: int = 50, request: Request = None):
    trace_id = request.state.trace_id
    messages = _MESSAGES.get(session_id, [])
    return ok({"messages": messages[-limit:]}, trace_id)
