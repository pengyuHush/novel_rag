"""Search and RAG schemas."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., description="用户问题", min_length=1)
    novel_ids: Optional[List[str]] = Field(None, description="限定的小说ID列表", alias="novelIds")
    top_k: int = Field(5, ge=1, le=10, alias="topK")
    include_references: bool = Field(True, alias="includeReferences")

    class Config:
        populate_by_name = True
        by_alias = True


class SearchReference(BaseModel):
    novel_id: Optional[str] = Field(None, alias="novelId")
    novel_title: Optional[str] = Field(None, alias="novelTitle")
    chapter_id: Optional[str] = Field(None, alias="chapterId")
    chapter_title: Optional[str] = Field(None, alias="chapterTitle")
    chapter_number: Optional[int] = Field(None, alias="chapterNumber")
    paragraph_index: Optional[int] = Field(None, alias="paragraphIndex")
    content: str
    relevance_score: float = Field(0.0, alias="relevanceScore")

    class Config:
        populate_by_name = True
        by_alias = True


class SearchTokenStats(BaseModel):
    """搜索Token统计"""

    total_tokens: int = Field(0, description="总Token消耗", alias="totalTokens")
    embedding_tokens: int = Field(0, description="Embedding Token消耗", alias="embeddingTokens")
    chat_tokens: int = Field(0, description="Chat Token消耗", alias="chatTokens")
    api_calls: int = Field(0, description="API调用次数", alias="apiCalls")
    estimated_cost: float = Field(0.0, description="预估费用（元）", alias="estimatedCost")

    class Config:
        populate_by_name = True
        by_alias = True


class SearchResponse(BaseModel):
    query: str
    answer: str
    references: List[SearchReference] = []
    elapsed: float
    token_stats: Optional[SearchTokenStats] = Field(None, description="Token统计", alias="tokenStats")

    class Config:
        populate_by_name = True
        by_alias = True


__all__ = ["SearchRequest", "SearchResponse", "SearchReference", "SearchTokenStats"]

