"""Character relationship graph schemas."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class CharacterNode(BaseModel):
    id: str
    name: str
    importance: float
    occurrences: int

    class Config:
        populate_by_name = True
        by_alias = True


class RelationshipEdge(BaseModel):
    source: str
    target: str
    relation: str
    weight: float
    evidence: List[str] = []

    class Config:
        populate_by_name = True
        by_alias = True


class CharacterGraphResponse(BaseModel):
    novel_id: str = Field(..., alias="novelId")
    characters: List[CharacterNode]
    relationships: List[RelationshipEdge]
    version: str = "1.0"

    class Config:
        populate_by_name = True
        by_alias = True


class CharacterGraphTaskResponse(BaseModel):
    message: str
    novel_id: str = Field(..., alias="novelId")
    status: str

    class Config:
        populate_by_name = True
        by_alias = True


__all__ = [
    "CharacterNode",
    "RelationshipEdge",
    "CharacterGraphResponse",
    "CharacterGraphTaskResponse",
]

