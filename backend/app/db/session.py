"""Database session and engine management."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.base import Base


engine = create_async_engine(settings.DATABASE_URL, future=True, echo=settings.DEBUG)
AsyncSessionLocal = async_sessionmaker[
    AsyncSession
](bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Create database tables."""

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = ["engine", "AsyncSessionLocal", "get_db_session", "init_db"]

