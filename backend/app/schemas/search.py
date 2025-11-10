"""Search and RAG schemas."""

from __future__ import annotations

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., description="用户问题", min_length=1)
    novel_ids: Optional[List[str]] = Field(None, description="限定的小说ID列表", alias="novelIds")
    top_k: int = Field(5, ge=1, le=10, alias="topK")
    include_references: bool = Field(True, alias="includeReferences")
    
    # 🔥 元数据过滤参数
    filter_characters: Optional[List[str]] = Field(None, description="过滤指定角色", alias="filterCharacters")
    filter_scene_type: Optional[str] = Field(None, description="过滤指定场景类型", alias="filterSceneType")
    filter_emotional_tone: Optional[str] = Field(None, description="过滤指定情感基调", alias="filterEmotionalTone")

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
    
    # 🔥 元数据字段（可选显示）
    characters: Optional[List[str]] = Field(None, description="角色列表")
    keywords: Optional[List[str]] = Field(None, description="关键词列表")
    scene_type: Optional[str] = Field(None, alias="sceneType", description="场景类型")
    emotional_tone: Optional[str] = Field(None, alias="emotionalTone", description="情感基调")

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


class StreamEvent(BaseModel):
    """流式事件基类（用于文档说明）"""
    
    type: Literal["references", "thinking", "answer", "token_stats", "done", "error"] = Field(
        ..., description="事件类型"
    )
    

class ReferencesEvent(StreamEvent):
    """引用数据事件"""
    
    type: Literal["references"] = "references"
    data: List[dict] = Field(..., description="引用列表")


class ThinkingEvent(StreamEvent):
    """思考过程事件"""
    
    type: Literal["thinking"] = "thinking"
    content: str = Field(..., description="思考过程片段")


class AnswerEvent(StreamEvent):
    """答案片段事件"""
    
    type: Literal["answer"] = "answer"
    content: str = Field(..., description="答案片段")


class TokenStatsEvent(StreamEvent):
    """Token统计事件"""
    
    type: Literal["token_stats"] = "token_stats"
    data: dict = Field(..., description="Token统计数据")


class DoneEvent(StreamEvent):
    """完成事件"""
    
    type: Literal["done"] = "done"


class ErrorEvent(StreamEvent):
    """错误事件"""
    
    type: Literal["error"] = "error"
    message: str = Field(..., description="错误信息")


__all__ = [
    "SearchRequest", 
    "SearchResponse", 
    "SearchReference", 
    "SearchTokenStats",
    "StreamEvent",
    "ReferencesEvent",
    "ThinkingEvent",
    "AnswerEvent",
    "TokenStatsEvent",
    "DoneEvent",
    "ErrorEvent"
]

