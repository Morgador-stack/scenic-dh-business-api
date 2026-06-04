"""中间件：trace_id 注入、请求日志、统一错误处理"""

import uuid
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings

logger = logging.getLogger("business-api")


class TraceMiddleware(BaseHTTPMiddleware):
    """为每个请求注入 trace_id，从上游继承或新建"""

    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("x-trace-id", f"trace_{uuid.uuid4().hex}")
        span_id = str(uuid.uuid4())[:8]

        request.state.trace_id = trace_id
        request.state.span_id = span_id

        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000

        response.headers["x-trace-id"] = trace_id
        response.headers["x-span-id"] = span_id
        response.headers["x-service"] = settings.SERVICE_NAME
        response.headers["x-elapsed-ms"] = f"{elapsed_ms:.1f}"

        logger.info(
            "request",
            extra={
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )
        return response


async def internal_auth_middleware(request: Request, call_next):
    """内部服务间鉴权校验（白名单模式：仅保护 /internal/ 路径）"""
    # 公开路径无需鉴权
    if request.url.path in ("/health", "/docs", "/redoc", "/openapi.json"):
        return await call_next(request)

    if request.url.path.startswith("/internal/"):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer ") or auth_header[7:] != settings.INTERNAL_SERVICE_TOKEN:
            return JSONResponse(
                status_code=401,
                content={
                    "code": 40100,
                    "message": "内部服务 token 无效",
                    "data": None,
                    "trace_id": getattr(request.state, "trace_id", "unknown"),
                },
            )
    return await call_next(request)
