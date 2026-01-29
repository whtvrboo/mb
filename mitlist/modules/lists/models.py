"""Lists module ORM models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import Base, BaseModel, TimestampMixin, VersionMixin


class ListType(str, Enum):
    """List type enumeration."""

    SHOPPING = "SHOPPING"
    TODO = "TODO"


class List(BaseModel, TimestampMixin):
    """
    List model - represents a shopping list or todo list.

    Uses optimistic locking via VersionMixin.
    """

    __tablename__ = "lists"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[ListType] = mapped_column(String(20), nullable=False)
    created_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    deadline: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    store_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    estimated_total: Mapped[Optional[float]] = mapped_column(nullable=True)
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)
    archived_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Optimistic locking
    version_id: Mapped[int] = mapped_column(nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version_id}

    # Relationships
    items: Mapped[list["Item"]] = relationship("Item", back_populates="list", cascade="all, delete-orphan")


class Item(BaseModel, TimestampMixin, VersionMixin):
    """
    Item model - represents an item in a list.

    Example of using with_for_update() for critical operations like inventory decrement.
    """

    __tablename__ = "items"

    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_value: Mapped[Optional[float]] = mapped_column(nullable=True)
    quantity_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    concept_id: Mapped[Optional[int]] = mapped_column(ForeignKey("common_item_concepts.id"), nullable=True)
    is_checked: Mapped[bool] = mapped_column(default=False, nullable=False)
    checked_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    price_estimate: Mapped[Optional[float]] = mapped_column(nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # HIGH, MEDIUM, LOW
    added_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Optimistic locking
    version_id: Mapped[int] = mapped_column(nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version_id}

    # Relationships
    list: Mapped["List"] = relationship("List", back_populates="items")
