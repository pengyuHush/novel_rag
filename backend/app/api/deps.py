"""Common FastAPI dependencies."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis
from app.db.session import get_db_session
from app.services.graph_service import GraphService
from app.services.novel_service import NovelService
from app.services.rag_service import RAGService
from app.services.system_service import SystemService
from app.services.text_processing_service import TextProcessingService

# 直接使用 get_db_session 作为依赖
get_session = get_db_session


async def get_novel_service(
    db: AsyncSession = Depends(get_session),
) -> AsyncGenerator[NovelService, None]:
    service = NovelService(db)
    yield service


async def get_text_processing_service(
    db: AsyncSession = Depends(get_session),
    redis_client: Redis = Depends(get_redis)
) -> AsyncGenerator[TextProcessingService, None]:
    yield TextProcessingService(session=db, redis_client=redis_client)


async def get_rag_service(
    redis_client: Redis = Depends(get_redis),
) -> AsyncGenerator[RAGService, None]:
    yield RAGService(redis_client=redis_client)


async def get_graph_service(
    db: AsyncSession = Depends(get_session),
) -> AsyncGenerator[GraphService, None]:
    yield GraphService(session=db)


async def get_system_service(
    db: AsyncSession = Depends(get_session),
    redis_client: Redis = Depends(get_redis)
) -> AsyncGenerator[SystemService, None]:
    yield SystemService(session=db, redis_client=redis_client)


__all__ = [
    "get_session",
    "get_novel_service",
    "get_text_processing_service",
    "get_rag_service",
    "get_graph_service",
    "get_system_service",
]

