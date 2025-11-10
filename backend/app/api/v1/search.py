"""RAG search API endpoints."""

from __future__ import annotations

import json
from fastapi import Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.router import APIRouter
from loguru import logger

from app.api.deps import get_rag_service
from app.schemas.search import SearchRequest, SearchResponse
from app.services.rag_service import RAGService

router = APIRouter()


@router.post("", response_model=SearchResponse)
async def search_novels(
    request: SearchRequest,
    service: RAGService = Depends(get_rag_service),
) -> SearchResponse:
    """Perform RAG-based semantic search on novel content."""
    try:
        return await service.search(request)
    except Exception as e:
        logger.exception("Search failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        ) from e


@router.post("/stream")
async def search_novels_stream(
    request: SearchRequest,
    service: RAGService = Depends(get_rag_service),
):
    """Perform RAG-based semantic search with streaming response."""
    
    async def event_generator():
        """Generate SSE events."""
        try:
            async for event in service.search_stream(request):
                # SSE格式：data: {json}\n\n
                event_json = json.dumps(event, ensure_ascii=False)
                yield f"data: {event_json}\n\n"
        except Exception as e:
            logger.exception("Stream search failed")
            error_event = {
                'type': 'error',
                'message': str(e)
            }
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用nginx缓冲
        }
    )


__all__ = ["router"]

