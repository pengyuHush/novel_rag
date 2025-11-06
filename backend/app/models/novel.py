"""Novel SQLAlchemy model."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Novel(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represent a novel entry."""

    __tablename__ = "novels"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)

    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0)
    chapter_count: Mapped[int] = mapped_column(Integer, default=0)

    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    encoding: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    has_graph: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_progress: Mapped[float] = mapped_column(Float, default=0.0)
    processing_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    chapters: Mapped[list["Chapter"]] = relationship(
        back_populates="novel", cascade="all, delete-orphan", lazy="selectin"
    )

    def mark_processing(self) -> None:
        self.status = "processing"

    def mark_completed(self) -> None:
        self.status = "completed"

    def mark_failed(self) -> None:
        self.status = "failed"


__all__ = ["Novel"]

