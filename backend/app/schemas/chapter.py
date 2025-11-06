"""Chapter schemas."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Chapter(BaseModel):
    id: str
    novel_id: str = Field(..., alias="novelId")
    chapter_number: int = Field(..., alias="chapterNumber")
    title: str
    start_position: int = Field(..., alias="startPosition")
    end_position: int = Field(..., alias="endPosition")
    word_count: int = Field(..., alias="wordCount")

    class Config:
        populate_by_name = True
        by_alias = True


class ChapterContentResponse(BaseModel):
    id: str
    novel_id: str = Field(..., alias="novelId")
    title: str
    chapter_number: int = Field(..., alias="chapterNumber")
    content: str
    paragraphs: List[str]

    class Config:
        populate_by_name = True
        by_alias = True


class ChapterListResponse(BaseModel):
    data: List[Chapter]


__all__ = ["Chapter", "ChapterListResponse", "ChapterContentResponse"]

