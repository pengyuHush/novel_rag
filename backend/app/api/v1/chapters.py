"""Chapter management API endpoints."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.core.router import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.repositories.chapter_repository import ChapterRepository
from app.repositories.novel_repository import NovelRepository
from app.schemas.chapter import Chapter, ChapterContentResponse, ChapterListResponse
from app.utils.text_processing import split_paragraphs

router = APIRouter()


@router.get("/{novel_id}/chapters", response_model=ChapterListResponse)
async def list_chapters(
    novel_id: str,
    db: AsyncSession = Depends(get_session),
) -> ChapterListResponse:
    """List all chapters for a novel."""
    novel_repo = NovelRepository(db)
    novel = await novel_repo.get(novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    chapter_repo = ChapterRepository(db)
    chapters = await chapter_repo.list_by_novel(novel_id)

    return ChapterListResponse(
        data=[Chapter(**ch.to_dict()) for ch in chapters]
    )


@router.get("/{novel_id}/chapters/{chapter_id}/content", response_model=ChapterContentResponse)
async def get_chapter_content(
    novel_id: str,
    chapter_id: str,
    db: AsyncSession = Depends(get_session),
) -> ChapterContentResponse:
    """Get content of a specific chapter."""
    chapter_repo = ChapterRepository(db)
    chapter = await chapter_repo.get(chapter_id)

    if not chapter or chapter.novel_id != novel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    content = await chapter_repo.get_content(novel_id, chapter)
    if not content:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter content not available")

    paragraphs = split_paragraphs(content)

    return ChapterContentResponse(
        id=chapter.id,
        novel_id=chapter.novel_id,
        title=chapter.title,
        chapter_number=chapter.chapter_number,
        content=content,
        paragraphs=paragraphs,
    )


__all__ = ["router"]

