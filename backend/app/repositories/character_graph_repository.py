"""Repository for character graph persistence."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharacterGraph


class CharacterGraphRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, novel_id: str) -> CharacterGraph | None:
        result = await self.session.scalars(
            select(CharacterGraph).where(CharacterGraph.novel_id == novel_id)
        )
        return result.first()

    async def upsert(self, graph: CharacterGraph) -> CharacterGraph:
        self.session.merge(graph)
        await self.session.flush()
        return graph

    async def delete(self, novel_id: str) -> None:
        """Delete character graph by novel_id."""
        graph = await self.get(novel_id)
        if graph:
            await self.session.delete(graph)
            await self.session.flush()


__all__ = ["CharacterGraphRepository"]

