"""Repository for search cache entries."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SearchCache


class SearchCacheRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, query_hash: str) -> SearchCache | None:
        result = await self.session.scalars(
            select(SearchCache).where(SearchCache.query_hash == query_hash)
        )
        return result.first()

    async def upsert(self, *, query_hash: str, query: str, result_str: str) -> None:
        cache = SearchCache(query_hash=query_hash, query=query, result=result_str)
        self.session.merge(cache)
        await self.session.flush()


__all__ = ["SearchCacheRepository"]

