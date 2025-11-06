"""Pydantic schemas exposed by the API."""

from .chapter import Chapter, ChapterListResponse
from .graph import CharacterGraphResponse, CharacterGraphTaskResponse
from .novel import (
    NovelCreate,
    NovelDetail,
    NovelListResponse,
    NovelStatusResponse,
    NovelSummary,
    NovelUpdate,
)
from .search import SearchReference, SearchRequest, SearchResponse
from .system import HealthResponse, SystemInfoResponse

__all__ = [
    "NovelCreate",
    "NovelDetail",
    "NovelListResponse",
    "NovelStatusResponse",
    "NovelSummary",
    "NovelUpdate",
    "Chapter",
    "ChapterListResponse",
    "CharacterGraphResponse",
    "CharacterGraphTaskResponse",
    "SearchRequest",
    "SearchResponse",
    "SearchReference",
    "HealthResponse",
    "SystemInfoResponse",
]

