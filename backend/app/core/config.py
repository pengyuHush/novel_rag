"""Application configuration using Pydantic settings."""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application configuration."""

    # General
    PROJECT_NAME: str = "小说RAG分析系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_V1_STR: str = "/api/v1"

    # CORS - 可以是逗号分隔的字符串或列表
    CORS_ORIGINS: str | List[str] = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./novel_rag.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "novel_embeddings"

    # Zhipu / ZAI API keys
    ZHIPU_API_KEY: str | None = None
    ZAI_API_KEY: str | None = None

    # Text processing configuration
    MAX_UPLOAD_SIZE_MB: int = 50
    MIN_WORD_COUNT: int = 1000
    MIN_CHINESE_RATIO: float = 0.6
    CHUNK_SIZE: int = 800  # 每个chunk的最大字符数
    CHUNK_OVERLAP: int = 100  # chunk之间的重叠字符数
    MAX_TOP_K: int = 8
    EMBEDDING_BATCH_SIZE: int = 6  # 单次embedding请求的最大文本数量

    # Background processing
    MAX_BACKGROUND_CONCURRENCY: int = 2

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


settings = get_settings()

__all__ = ["Settings", "settings", "get_settings"]

