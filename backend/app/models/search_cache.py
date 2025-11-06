"""Search cache model to store recent RAG results."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class SearchCache(TimestampMixin, Base):
    """Cache RAG search responses for quick retrieval."""

    __tablename__ = "search_cache"

    query_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    result: Mapped[str] = mapped_column(Text, nullable=False)


__all__ = ["SearchCache"]

