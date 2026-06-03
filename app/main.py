"""scenic-dh-business-api — 景区业务域接口

FastAPI 应用入口。负责景点、路线、会话、消息、到达事件、反馈的结构化数据。
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware import TraceMiddleware, internal_auth_middleware

# 日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='{"time":"%(asctime)s","level":"%(levelname)s","service":"%(name)s","message":"%(message)s"}',
    stream=sys.stdout,
)
logger = logging.getLogger("business-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"{settings.SERVICE_NAME} v{settings.SERVICE_VERSION} starting on port {settings.PORT}")
    yield
    logger.info(f"{settings.SERVICE_NAME} shutting down")


app = FastAPI(
    title="scenic-dh-business-api",
    version=settings.SERVICE_VERSION,
    description="景区业务域接口 — 景点、路线、会话、消息、到达事件、反馈",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 自定义中间件
app.add_middleware(TraceMiddleware)
app.middleware("http")(internal_auth_middleware)


# ═══════════════════════════════════════════
# Health
# ═══════════════════════════════════════════
@app.get("/health", tags=["Health"])
def health():
    from app.schemas.common import ok
    from fastapi import Request
    import inspect

    # 尝试获取 request context；在非请求上下文中回退
    trace_id = "startup-check"

    return ok(
        {
            "status": "ok",
            "version": settings.SERVICE_VERSION,
            "dependencies": {
                "rag_service": settings.RAG_SERVICE_URL,
                "avatar_orchestrator": settings.AVATAR_ORCHESTRATOR_URL,
            },
        },
        trace_id,
    )


# ═══════════════════════════════════════════
# Routers（逐步挂载）
# ═══════════════════════════════════════════
from app.routers import spots, routes, sessions, messages, arrivals, feedback, scenic, rag_proxy, internal  # noqa: E402

app.include_router(spots.router, prefix="/v1")
app.include_router(routes.router, prefix="/v1")
app.include_router(sessions.router, prefix="/v1")
app.include_router(messages.router, prefix="/v1")
app.include_router(arrivals.router, prefix="/v1")
app.include_router(feedback.router, prefix="/v1")
app.include_router(scenic.router, prefix="/v1")
app.include_router(rag_proxy.router, prefix="/v1")
app.include_router(internal.router)  # 不带 prefix，路径自带 /internal/v1/
