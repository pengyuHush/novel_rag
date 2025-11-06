"""System health and info service."""

from __future__ import annotations

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.qdrant import get_qdrant_client
from app.schemas.system import HealthComponent, HealthResponse, SystemInfoResponse


class SystemService:
    """Provide system health checks and info."""

    def __init__(self, session: AsyncSession, redis_client: Redis | None = None):
        self.session = session
        self.redis = redis_client

    async def health_check(self) -> HealthResponse:
        """Check health of all components."""
        components = {}

        # Database
        try:
            await self.session.execute(text("SELECT 1"))
            components["database"] = HealthComponent(status="healthy", detail="Connected")
        except Exception as e:
            components["database"] = HealthComponent(status="unhealthy", detail=str(e))

        # Redis
        if self.redis:
            try:
                await self.redis.ping()
                components["redis"] = HealthComponent(status="healthy", detail="Connected")
            except Exception as e:
                components["redis"] = HealthComponent(status="unhealthy", detail=str(e))
        else:
            components["redis"] = HealthComponent(status="disabled", detail="Not configured")

        # Qdrant
        try:
            qdrant = get_qdrant_client()
            collections = qdrant.get_collections()
            components["qdrant"] = HealthComponent(
                status="healthy", detail=f"{len(collections.collections)} collections"
            )
        except Exception as e:
            components["qdrant"] = HealthComponent(status="unhealthy", detail=str(e))

        # GLM API
        if settings.ZAI_API_KEY or settings.ZHIPU_API_KEY:
            components["glm_api"] = HealthComponent(status="configured", detail="API key configured")
        else:
            components["glm_api"] = HealthComponent(status="disabled", detail="API key not configured")

        overall = "healthy" if all(c.status in ("healthy", "configured") for c in components.values()) else "degraded"
        return HealthResponse(status=overall, components=components)

    async def system_info(self) -> SystemInfoResponse:
        """Return system information."""
        return SystemInfoResponse(
            project_name=settings.PROJECT_NAME,
            version=settings.VERSION,
            description="小说 RAG 分析系统后端",
            features={
                "rag_search": True,
                "character_graph": True,
                "chapter_management": True,
                "file_upload": True,
            },
        )


__all__ = ["SystemService"]

