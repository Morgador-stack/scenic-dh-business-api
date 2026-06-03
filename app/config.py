"""scenic-dh-business-api 配置"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 服务
    SERVICE_NAME: str = "scenic-dh-business-api"
    SERVICE_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    DEBUG: bool = False

    # 数据库
    DATABASE_URL: str = "sqlite:///./scenic_business.db"

    # 上游服务
    RAG_SERVICE_URL: str = "http://localhost:8003/api/v1"
    AVATAR_ORCHESTRATOR_URL: str = "http://localhost:8004/v1"

    # 内部服务 token
    SERVICE_TOKEN: str = "svc-dev-token"

    # 日志
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # 默认景区
    DEFAULT_SCENIC_ID: str = "SA-001"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
