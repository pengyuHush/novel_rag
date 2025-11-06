"""Qdrant client helper."""

from __future__ import annotations

from functools import lru_cache

from qdrant_client import QdrantClient

from app.core.config import settings


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    # Disable version check to avoid warnings about minor version differences
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        prefer_grpc=False,
        timeout=30.0,
    )


__all__ = ["get_qdrant_client"]

