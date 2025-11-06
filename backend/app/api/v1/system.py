"""System management API endpoints."""

from __future__ import annotations

from fastapi import Depends

from app.core.router import APIRouter

from app.api.deps import get_system_service
from app.schemas.system import HealthResponse, SystemInfoResponse
from app.services.system_service import SystemService

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(
    service: SystemService = Depends(get_system_service),
) -> HealthResponse:
    """Check system health status."""
    return await service.health_check()


@router.get("/info", response_model=SystemInfoResponse)
async def system_info(
    service: SystemService = Depends(get_system_service),
) -> SystemInfoResponse:
    """Get system information."""
    return await service.system_info()


__all__ = ["router"]

