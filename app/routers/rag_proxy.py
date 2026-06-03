"""RAG 查询代理 — 前端通过 business-api 访问 RAG 服务"""

import httpx
from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.schemas.common import ok, err
from app.config import settings

router = APIRouter(tags=["RAG Proxy"])

RAG_QUERY_URL = f"{settings.RAG_SERVICE_URL}/api/v1/rag/query"
RAG_HEALTH_URL = f"{settings.RAG_SERVICE_URL}/api/v1/rag/health"


class RagQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    filters: dict | None = None


@router.post("/rag/query")
async def rag_query(body: RagQueryRequest, request: Request):
    """代理 RAG 语义检索，前端统一入口"""
    trace_id = request.state.trace_id

    payload = {"query": body.query, "top_k": body.top_k}
    if body.filters:
        payload["filters"] = body.filters

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                RAG_QUERY_URL,
                json=payload,
                headers={"X-Trace-Id": trace_id, "Content-Type": "application/json"},
            )
            resp.raise_for_status()
            rag_data = resp.json()
    except httpx.ConnectError:
        return err(50300, "RAG 服务不可达", trace_id)
    except httpx.TimeoutException:
        return err(50401, "RAG 检索超时", trace_id)
    except Exception as e:
        return err(50000, f"RAG 代理异常: {str(e)}", trace_id)

    # 透传 RAG 响应，保持格式一致
    if rag_data.get("code") == 0:
        return ok(rag_data["data"], trace_id)
    else:
        return err(
            rag_data.get("code", 50000),
            rag_data.get("message", "RAG 返回错误"),
            trace_id,
        )


@router.get("/rag/health")
async def rag_health(request: Request):
    """检查 RAG 服务连通性"""
    trace_id = request.state.trace_id
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(RAG_HEALTH_URL, headers={"X-Trace-Id": trace_id})
            return ok({"rag_status": "ok", "rag_detail": resp.json()}, trace_id)
    except Exception:
        return ok({"rag_status": "unreachable", "rag_detail": None}, trace_id)
