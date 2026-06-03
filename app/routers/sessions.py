"""游客会话接口"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err

router = APIRouter(tags=["Sessions"])

# 内存存储（MVP 阶段；后续换 SQLite）
_SESSIONS: dict[str, dict] = {}


class CreateSessionRequest(BaseModel):
    profile: dict | None = None
    source: str = "web"
    language: str = "zh"


class PatchSessionRequest(BaseModel):
    currentSpotId: str | None = None
    currentRouteId: str | None = None
    profile: dict | None = None


@router.post("/sessions")
def create_session(body: CreateSessionRequest, request: Request):
    trace_id = request.state.trace_id
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    session = {
        "id": session_id,
        "profile": body.profile or {"language": body.language, "interests": [], "groupSize": 1, "hasChildren": False},
        "source": body.source,
        "currentSpotId": None,
        "currentRouteId": None,
        "status": "active",
        "createdAt": now,
        "updatedAt": now,
    }
    _SESSIONS[session_id] = session
    return ok({"sessionId": session_id, "status": "active"}, trace_id)


@router.get("/sessions/{session_id}")
def get_session(session_id: str, request: Request):
    trace_id = request.state.trace_id
    session = _SESSIONS.get(session_id)
    if not session:
        return err(40403, f"会话 {session_id} 不存在", trace_id)
    return ok(session, trace_id)


@router.patch("/sessions/{session_id}")
def patch_session(session_id: str, body: PatchSessionRequest, request: Request):
    trace_id = request.state.trace_id
    session = _SESSIONS.get(session_id)
    if not session:
        return err(40403, f"会话 {session_id} 不存在", trace_id)
    if body.currentSpotId is not None:
        session["currentSpotId"] = body.currentSpotId
    if body.currentRouteId is not None:
        session["currentRouteId"] = body.currentRouteId
    if body.profile is not None:
        session["profile"] = body.profile
    session["updatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    _SESSIONS[session_id] = session
    return ok(session, trace_id)
