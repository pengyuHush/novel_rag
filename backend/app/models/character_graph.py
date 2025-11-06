"""Character relationship graph model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CharacterGraph(TimestampMixin, Base):
    """Persist generated character relationship graphs."""

    __tablename__ = "character_graphs"

    novel_id: Mapped[str] = mapped_column(
        ForeignKey("novels.id", ondelete="CASCADE"), primary_key=True
    )
    characters: Mapped[list[dict]] = mapped_column(JSON, default=list)
    relationships: Mapped[list[dict]] = mapped_column(JSON, default=list)
    version: Mapped[str] = mapped_column(Text, default="1.0")


__all__ = ["CharacterGraph"]

