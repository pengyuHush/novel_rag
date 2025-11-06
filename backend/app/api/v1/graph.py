"""Character graph API endpoints."""

from __future__ import annotations

import asyncio

from fastapi import BackgroundTasks, Depends, HTTPException, status

from app.core.router import APIRouter
from loguru import logger

from app.api.deps import get_graph_service
from app.schemas.graph import CharacterGraphResponse, CharacterGraphTaskResponse
from app.services.graph_service import GraphService

router = APIRouter()


@router.get("/{novel_id}/graph", response_model=CharacterGraphResponse)
async def get_character_graph(
    novel_id: str,
    service: GraphService = Depends(get_graph_service),
) -> CharacterGraphResponse:
    """Get character relationship graph for a novel."""
    graph = await service.get_graph(novel_id)
    if not graph:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Graph not found. Generate it first.")
    return graph


@router.post("/{novel_id}/graph", response_model=CharacterGraphTaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_character_graph(
    novel_id: str,
    background_tasks: BackgroundTasks = None,
    service: GraphService = Depends(get_graph_service),
) -> CharacterGraphTaskResponse:
    """Generate character relationship graph."""

    async def generate_task(novel_id: str):
        try:
            await service.generate_graph(novel_id)
        except Exception as e:
            logger.exception(f"Graph generation failed for novel {novel_id}")

    if background_tasks:
        background_tasks.add_task(generate_task, novel_id)
    else:
        asyncio.create_task(generate_task(novel_id))

    return CharacterGraphTaskResponse(
        message="人物关系图谱生成任务已启动",
        novel_id=novel_id,
        status="processing",
    )


@router.delete("/{novel_id}/graph", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character_graph(
    novel_id: str,
    service: GraphService = Depends(get_graph_service),
) -> None:
    """Delete character relationship graph."""
    await service.delete_graph(novel_id)


__all__ = ["router"]

