"""Novel-related Pydantic schemas."""

from __future__ import annotations

import datetime as dt
from typing import Any, List, Optional

from pydantic import BaseModel, Field, validator

from app.schemas.common import Pagination


class NovelBase(BaseModel):
    title: str = Field(..., description="小说名称", min_length=1, max_length=255)
    author: Optional[str] = Field(None, description="作者", max_length=255)
    description: Optional[str] = Field(None, description="小说简介")
    tags: List[str] = Field(default_factory=list, description="标签列表")


class NovelCreate(NovelBase):
    pass


class NovelUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class NovelSummary(NovelBase):
    id: str
    word_count: int = Field(0, alias="wordCount")
    chapter_count: int = Field(0, alias="chapterCount")
    status: str
    encoding: Optional[str] = None
    has_graph: bool = Field(False, alias="hasGraph")
    processing_progress: float = Field(0.0, alias="processingProgress")
    processing_message: Optional[str] = Field(None, alias="processingMessage")
    imported_at: dt.datetime = Field(..., alias="importedAt")
    updated_at: dt.datetime = Field(..., alias="updatedAt")
    
    # Token使用统计（智谱AI真实消耗）
    total_tokens_used: int = Field(0, alias="totalTokensUsed", description="总Token消耗")
    embedding_tokens_used: int = Field(0, alias="embeddingTokensUsed", description="Embedding Token消耗")
    chat_tokens_used: int = Field(0, alias="chatTokensUsed", description="聊天Token消耗")
    api_calls_count: int = Field(0, alias="apiCallsCount", description="API调用次数")
    estimated_cost: float = Field(0.0, alias="estimatedCost", description="预估费用（元）")

    class Config:
        populate_by_name = True
        by_alias = True


class NovelDetail(NovelSummary):
    content: Optional[str] = None
    file_path: Optional[str] = Field(None, alias="filePath")
    chapters: List[Any] = Field(default_factory=list, description="章节列表")


class NovelListResponse(BaseModel):
    data: List[NovelSummary]
    pagination: Pagination


class TokenStats(BaseModel):
    """Token使用统计详情."""
    
    total_tokens: int = Field(0, alias="totalTokens", description="总Token消耗")
    embedding_tokens: int = Field(0, alias="embeddingTokens", description="Embedding Token消耗")
    chat_tokens: int = Field(0, alias="chatTokens", description="聊天Token消耗（关系图谱生成等）")
    api_calls: int = Field(0, alias="apiCalls", description="API调用总次数")
    estimated_cost: float = Field(0.0, alias="estimatedCost", description="预估费用（元）")
    
    class Config:
        populate_by_name = True
        by_alias = True


class NovelStatusResponse(BaseModel):
    novel_id: str = Field(..., alias="novelId")
    status: str
    progress: float = Field(0.0, ge=0.0, le=100.0, description="处理进度(0-100)")
    message: Optional[str] = None
    token_stats: Optional[TokenStats] = Field(None, alias="tokenStats", description="Token使用统计")

    @validator("progress")
    def round_progress(cls, value: float) -> float:  # noqa: N805
        """将进度四舍五入到2位小数并钳制在0-100范围"""
        return round(max(0.0, min(100.0, value)), 2)

    class Config:
        populate_by_name = True
        by_alias = True


class NovelProcessingResponse(BaseModel):
    message: str
    novel_id: str = Field(..., alias="novelId")
    status: str
    estimated_time: int | None = Field(None, alias="estimatedTime")

    class Config:
        populate_by_name = True
        by_alias = True


__all__ = [
    "NovelCreate",
    "NovelUpdate",
    "NovelSummary",
    "NovelDetail",
    "NovelListResponse",
    "NovelStatusResponse",
    "NovelProcessingResponse",
    "TokenStats",
]

