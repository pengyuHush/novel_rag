"""API routers package."""

from app.api.v1 import router as v1_router
from app.core.config import settings
from app.core.router import APIRouter


api_router = APIRouter()
api_router.include_router(v1_router, prefix=settings.API_V1_STR)


__all__ = ["api_router"]

