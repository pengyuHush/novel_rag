"""SQLAlchemy declarative base and common mixins."""

from __future__ import annotations

import datetime as dt
from typing import Any

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """Base declarative class."""


class TimestampMixin:
    """Provide created/updated timestamps."""

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class UUIDPrimaryKeyMixin:
    """Provide a string UUID primary key."""

    @declared_attr
    def id(cls) -> Mapped[str]:
        from uuid import uuid4

        return mapped_column(
            primary_key=True,
            default=lambda: uuid4().hex,
        )


__all__ = ["Base", "TimestampMixin", "UUIDPrimaryKeyMixin"]

