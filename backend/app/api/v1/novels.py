"""Novel management API endpoints."""

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import BackgroundTasks, Depends, File, HTTPException, UploadFile, status

from app.core.router import APIRouter
from loguru import logger

from app.api.deps import get_novel_service, get_text_processing_service
from app.core.exceptions import InvalidFileError, NovelNotFoundError
from app.schemas.common import MessageResponse
from app.schemas.novel import (
    NovelCreate,
    NovelDetail,
    NovelListResponse,
    NovelProcessingResponse,
    NovelStatusResponse,
    NovelUpdate,
)
from app.services.novel_service import NovelService
from app.services.text_processing_service import TextProcessingService
from app.utils.file_storage import delete_novel_file, save_upload_file

router = APIRouter()


@router.get("", response_model=NovelListResponse)
async def list_novels(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    sort_by: str = "-created_at",
    service: NovelService = Depends(get_novel_service),
) -> NovelListResponse:
    """List all novels with pagination."""
    return await service.list_novels(page=page, page_size=page_size, search=search, sort_by=sort_by)


@router.post("", response_model=NovelDetail, status_code=status.HTTP_201_CREATED)
async def create_novel(
    data: NovelCreate,
    service: NovelService = Depends(get_novel_service),
) -> NovelDetail:
    """Create a new novel entry."""
    return await service.create_novel(data)


@router.get("/{novel_id}", response_model=NovelDetail)
async def get_novel(
    novel_id: str,
    service: NovelService = Depends(get_novel_service),
) -> NovelDetail:
    """Get novel details by ID."""
    novel = await service.get_novel(novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    return novel


@router.put("/{novel_id}", response_model=NovelDetail)
async def update_novel(
    novel_id: str,
    data: NovelUpdate,
    service: NovelService = Depends(get_novel_service),
) -> NovelDetail:
    """Update novel metadata."""
    novel = await service.update_novel(novel_id, data)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    return novel


@router.delete("/{novel_id}", response_model=MessageResponse)
async def delete_novel(
    novel_id: str,
    service: NovelService = Depends(get_novel_service),
) -> MessageResponse:
    """Delete a novel and all associated data."""
    success = await service.delete_novel(novel_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    # Clean up file storage
    delete_novel_file(novel_id)

    return MessageResponse(message="Novel deleted successfully")


@router.post("/{novel_id}/upload", response_model=NovelProcessingResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_novel_file(
    novel_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    novel_service: NovelService = Depends(get_novel_service),
    text_service: TextProcessingService = Depends(get_text_processing_service),
) -> NovelProcessingResponse:
    """Upload and process a novel text file."""
    novel = await novel_service.get_novel(novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    # Save file
    try:
        file_path = await save_upload_file(novel_id, file)
    except Exception as e:
        logger.exception(f"Failed to save file for novel {novel_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"File save failed: {e}") from e

    # Process in background
    async def process_with_progress(novel_id: str, file_path: Path):
        async def progress_callback(progress: float, message: str):
            await novel_service.update_processing_progress(novel_id, progress=progress, message=message)

        try:
            await text_service.process_novel(novel_id, file_path, progress_callback)
        except InvalidFileError as e:
            logger.warning(f"Invalid file for novel {novel_id}: {e.message}")
            await novel_service.mark_status(novel_id, "failed")
        except Exception as e:
            logger.exception(f"Processing failed for novel {novel_id}")
            await novel_service.mark_status(novel_id, "failed")

    if background_tasks:
        background_tasks.add_task(process_with_progress, novel_id, file_path)
    else:
        asyncio.create_task(process_with_progress(novel_id, file_path))

    return NovelProcessingResponse(
        message="文件上传成功，正在处理中",
        novel_id=novel_id,
        status="processing",
        estimated_time=120,
    )


@router.get("/{novel_id}/status", response_model=NovelStatusResponse)
async def get_novel_status(
    novel_id: str,
    service: NovelService = Depends(get_novel_service),
) -> NovelStatusResponse:
    """Get novel processing status."""
    novel = await service.get_novel(novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

    return NovelStatusResponse(
        novel_id=novel_id,
        status=novel.status,
        progress=novel.processing_progress,
        message=novel.processing_message,
    )


__all__ = ["router"]

