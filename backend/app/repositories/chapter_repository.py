"""Repository for chapter operations."""

from __future__ import annotations

from typing import Iterable, List, Optional

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chapter, Novel


class ChapterRepository:
    """Persistence helper for chapters."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_novel(self, novel_id: str) -> List[Chapter]:
        query: Select[tuple[Chapter]] = (
            select(Chapter)
            .where(Chapter.novel_id == novel_id)
            .order_by(Chapter.chapter_number)
        )
        result = await self.session.scalars(query)
        return list(result)

    async def bulk_create(self, chapters: Iterable[Chapter]) -> None:
        self.session.add_all(list(chapters))
        await self.session.flush()

    async def delete_by_novel(self, novel_id: str) -> None:
        chapters = await self.session.scalars(select(Chapter).where(Chapter.novel_id == novel_id))
        for chapter in chapters:
            await self.session.delete(chapter)

    async def get(self, chapter_id: str) -> Optional[Chapter]:
        return await self.session.get(Chapter, chapter_id)

    async def get_content(self, novel_id: str, chapter: Chapter) -> Optional[str]:
        novel = await self.session.get(Novel, novel_id)
        if novel and novel.content:
            return novel.content[chapter.start_position : chapter.end_position]
        return None


__all__ = ["ChapterRepository"]

