"""Service layer for novel operations."""

from __future__ import annotations

from math import ceil
from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import ChapterRepository, NovelRepository
from app.schemas.chapter import Chapter
from app.schemas.common import Pagination
from app.schemas.novel import NovelCreate, NovelDetail, NovelListResponse, NovelSummary, NovelUpdate


class NovelService:
    def __init__(self, session: AsyncSession):
        self.repo = NovelRepository(session)
        self.chapter_repo = ChapterRepository(session)
        self.session = session

    async def list_novels(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        sort_by: str = "-created_at",
    ) -> NovelListResponse:
        novels, total = await self.repo.list(
            page=page, page_size=page_size, search=search, sort_by=sort_by
        )
        summaries = [self._to_summary(novel) for novel in novels]
        pagination = Pagination(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if page_size else 0,
        )
        return NovelListResponse(data=summaries, pagination=pagination)

    async def get_novel(self, novel_id: str) -> NovelDetail | None:
        novel = await self.repo.get(novel_id)
        if not novel:
            return None
        
        # Get chapters for this novel
        chapters_data = await self.chapter_repo.list_by_novel(novel_id)
        chapters = [
            Chapter(
                id=ch.id,
                novel_id=ch.novel_id,
                chapter_number=ch.chapter_number,
                title=ch.title,
                start_position=ch.start_position,
                end_position=ch.end_position,
                word_count=ch.word_count,
            )
            for ch in chapters_data
        ]
        
        summary = self._to_summary(novel)
        return NovelDetail(**summary.model_dump(), content=novel.content, file_path=novel.file_path, chapters=chapters)

    async def create_novel(self, data: NovelCreate) -> NovelDetail:
        novel = await self.repo.create(
            title=data.title,
            author=data.author,
            description=data.description,
            tags=data.tags,
        )
        await self.session.commit()
        # Refresh the object to ensure all fields are loaded
        await self.session.refresh(novel)
        
        # Get chapters (will be empty for newly created novel)
        chapters_data = await self.chapter_repo.list_by_novel(novel.id)
        chapters = [
            Chapter(
                id=ch.id,
                novel_id=ch.novel_id,
                chapter_number=ch.chapter_number,
                title=ch.title,
                start_position=ch.start_position,
                end_position=ch.end_position,
                word_count=ch.word_count,
            )
            for ch in chapters_data
        ]
        
        # Convert to summary and detail in the same session
        summary = self._to_summary(novel)
        return NovelDetail(**summary.model_dump(), content=novel.content, file_path=novel.file_path, chapters=chapters)

    async def update_novel(self, novel_id: str, data: NovelUpdate) -> NovelDetail | None:
        novel = await self.repo.get(novel_id)
        if not novel:
            return None
        await self.repo.update(
            novel,
            title=data.title,
            author=data.author,
            description=data.description,
            tags=data.tags if data.tags is not None else novel.tags,
        )
        await self.session.commit()
        # Refresh the object to get updated values
        await self.session.refresh(novel)
        
        # Get chapters
        chapters_data = await self.chapter_repo.list_by_novel(novel_id)
        chapters = [
            Chapter(
                id=ch.id,
                novel_id=ch.novel_id,
                chapter_number=ch.chapter_number,
                title=ch.title,
                start_position=ch.start_position,
                end_position=ch.end_position,
                word_count=ch.word_count,
            )
            for ch in chapters_data
        ]
        
        # Convert to summary and detail in the same session
        summary = self._to_summary(novel)
        return NovelDetail(**summary.model_dump(), content=novel.content, file_path=novel.file_path, chapters=chapters)

    async def delete_novel(self, novel_id: str) -> bool:
        novel = await self.repo.get(novel_id)
        if not novel:
            return False
        await self.repo.delete(novel)
        await self.session.commit()
        return True

    async def mark_status(self, novel_id: str, status: str) -> None:
        novel = await self.repo.get(novel_id)
        if not novel:
            return
        await self.repo.update_status(novel, status)
        await self.session.commit()

    async def update_processing_stats(
        self,
        novel_id: str,
        *,
        word_count: int,
        chapter_count: int,
        encoding: str | None,
        file_size: int | None,
        file_path: str | None,
    ) -> None:
        novel = await self.repo.get(novel_id)
        if not novel:
            return
        await self.repo.update_processing_stats(
            novel,
            word_count=word_count,
            chapter_count=chapter_count,
            encoding=encoding,
            file_size=file_size,
            file_path=file_path,
        )
        await self.session.commit()

    async def update_processing_progress(
        self,
        novel_id: str,
        *,
        progress: float,
        message: str | None = None,
    ) -> None:
        novel = await self.repo.get(novel_id)
        if not novel:
            return
        await self.repo.set_processing_progress(novel, progress=progress, message=message)
        await self.session.commit()

    def _to_summary(self, novel) -> NovelSummary:
        return NovelSummary(
            id=novel.id,
            title=novel.title,
            author=novel.author,
            description=novel.description,
            tags=novel.tags or [],
            word_count=novel.word_count,
            chapter_count=novel.chapter_count,
            status=novel.status,
            encoding=novel.encoding,
            has_graph=novel.has_graph,
            processing_progress=novel.processing_progress,
            processing_message=novel.processing_message,
            imported_at=novel.created_at,  # Map created_at to imported_at
            updated_at=novel.updated_at,
        )


__all__ = ["NovelService"]

