"""Redis client utilities."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from redis.asyncio import Redis

from app.core.config import settings


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_redis() -> Redis:
    client = get_redis_client()
    try:
        yield client
    finally:
        pass


async def close_redis() -> None:
    client: Optional[Redis] = get_redis_client()
    if client:
        await client.aclose()


__all__ = ["get_redis_client", "get_redis", "close_redis"]

