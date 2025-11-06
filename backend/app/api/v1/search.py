"""RAG search API endpoints."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status

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


__all__ = ["router"]

