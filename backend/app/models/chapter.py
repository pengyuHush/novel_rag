
"""Chapter SQLAlchemy model."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Chapter(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represent a novel chapter."""

    __tablename__ = "chapters"

    novel_id: Mapped[str] = mapped_column(ForeignKey("novels.id", ondelete="CASCADE"), index=True)
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    start_position: Mapped[int] = mapped_column(Integer, nullable=False)
    end_position: Mapped[int] = mapped_column(Integer, nullable=False)
    word_count: Mapped[int] = mapped_column(Integer, default=0)

    novel: Mapped["Novel"] = relationship(back_populates="chapters")

    def to_dict(self) -> dict[str, Optional[int | str]]:
        return {
            "id": self.id,
            "novel_id": self.novel_id,
            "chapter_number": self.chapter_number,
            "title": self.title,
            "start_position": self.start_position,
            "end_position": self.end_position,
            "word_count": self.word_count,
        }


__all__ = ["Chapter"]
