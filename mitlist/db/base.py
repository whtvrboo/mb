"""SQLAlchemy declarative base and shared mixins."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


class TimestampMixin:
    """Mixin adding created_at and updated_at timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class VersionMixin:
    """
    Mixin adding optimistic locking via version_id column.

    Usage:
        class MyModel(Base, VersionMixin):
            __mapper_args__ = {"version_id_col": MyModel.version_id}
            ...
    """

    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class BaseModel(Base, TimestampMixin):
    """
    Base model with common fields: id, created_at, updated_at.

    All models should inherit from this or add TimestampMixin.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
