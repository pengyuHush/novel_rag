"""Repository for Novel model."""

from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Novel


class NovelRepository:
    """Persistence operations for novels."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sort_by: str = "-created_at",
    ) -> tuple[list[Novel], int]:
        query: Select[tuple[Novel]] = select(Novel)
        count_query = select(func.count(Novel.id))

        if search:
            pattern = f"%{search}%"
            criterion = Novel.title.ilike(pattern) | Novel.author.ilike(pattern)
            query = query.where(criterion)
            count_query = count_query.where(criterion)

        sort_field = Novel.created_at
        if sort_by.startswith("-"):
            sort_field = getattr(Novel, sort_by[1:], Novel.created_at).desc()
        else:
            sort_field = getattr(Novel, sort_by, Novel.created_at)

        query = query.order_by(sort_field)

        total = await self.session.scalar(count_query)
        offset = (page - 1) * page_size
        result = await self.session.scalars(query.offset(offset).limit(page_size))
        novels = list(result)
        return novels, int(total or 0)

    async def get(self, novel_id: str) -> Optional[Novel]:
        return await self.session.get(Novel, novel_id)

    async def create(self, *, title: str, author: str | None, description: str | None, tags: Iterable[str]) -> Novel:
        novel = Novel(
            title=title,
            author=author,
            description=description,
            tags=list(tags),
        )
        self.session.add(novel)
        await self.session.flush()
        return novel

    async def update(self, novel: Novel, **kwargs) -> Novel:
        for key, value in kwargs.items():
            if hasattr(novel, key) and value is not None:
                setattr(novel, key, value)
        await self.session.flush()
        return novel

    async def delete(self, novel: Novel) -> None:
        await self.session.delete(novel)

    async def update_status(self, novel: Novel, status: str) -> Novel:
        novel.status = status
        await self.session.flush()
        return novel

    async def update_processing_stats(
        self,
        novel: Novel,
        *,
        word_count: int,
        chapter_count: int,
        encoding: str | None,
        file_size: int | None,
        file_path: str | None,
    ) -> Novel:
        novel.word_count = word_count
        novel.chapter_count = chapter_count
        novel.encoding = encoding
        novel.file_size = file_size
        novel.file_path = file_path
        await self.session.flush()
        return novel

    async def set_processing_progress(
        self,
        novel: Novel,
        *,
        progress: float,
        message: str | None = None,
    ) -> Novel:
        novel.processing_progress = max(0.0, min(1.0, progress))
        novel.processing_message = message
        await self.session.flush()
        return novel


__all__ = ["NovelRepository"]

