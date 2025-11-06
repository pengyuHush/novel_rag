"""Versioned API router."""

from app.core.router import APIRouter

from .chapters import router as chapters_router
from .graph import router as graph_router
from .novels import router as novels_router
from .search import router as search_router
from .system import router as system_router


router = APIRouter()
router.include_router(novels_router, prefix="/novels", tags=["novels"])
router.include_router(chapters_router, prefix="/novels", tags=["chapters"])
router.include_router(graph_router, prefix="/novels", tags=["graph"])
router.include_router(search_router, prefix="/search", tags=["search"])
router.include_router(system_router, prefix="/system", tags=["system"])


__all__ = ["router"]

