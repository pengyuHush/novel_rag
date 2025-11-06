"""Common schema definitions."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    page: int = 1
    page_size: int = Field(20, alias="pageSize")
    total: int = 0
    total_pages: int = Field(0, alias="totalPages")

    class Config:
        populate_by_name = True
        by_alias = True


class MessageResponse(BaseModel):
    message: str

    class Config:
        populate_by_name = True
        by_alias = True


__all__ = ["Pagination", "MessageResponse"]

