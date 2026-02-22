"""Lists module ORM models."""

from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import BaseModel, TimestampMixin, VersionMixin


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

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[ListType] = mapped_column(String(20), nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    deadline: Mapped[datetime | None] = mapped_column(nullable=True)
    store_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    estimated_total: Mapped[float | None] = mapped_column(nullable=True)
    is_archived: Mapped[bool] = mapped_column(default=False, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Optimistic locking
    version_id: Mapped[int] = mapped_column(nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version_id}
    __table_args__ = (Index("ix_lists_group_id_id", "group_id", "id"),)

    # Relationships
    items: Mapped[list["Item"]] = relationship("Item", back_populates="list", cascade="all, delete-orphan")


class ListShare(BaseModel, TimestampMixin):
    """List share - share list with non-group members."""

    __tablename__ = "list_shares"

    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id"), nullable=False, index=True)
    share_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    can_edit: Mapped[bool] = mapped_column(default=False, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)


class InventoryItem(BaseModel, TimestampMixin):
    """Inventory item - pantry tracking with expiration."""

    __tablename__ = "inventory_items"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    location_id: Mapped[int | None] = mapped_column(ForeignKey("locations.id"), nullable=True)
    concept_id: Mapped[int | None] = mapped_column(ForeignKey("common_item_concepts.id"), nullable=True)
    quantity_value: Mapped[float | None] = mapped_column(nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    expiration_date: Mapped[datetime | None] = mapped_column(nullable=True)
    opened_date: Mapped[datetime | None] = mapped_column(nullable=True)
    restock_threshold: Mapped[float | None] = mapped_column(nullable=True)

    __table_args__ = (Index("ix_inventory_items_group_id_id", "group_id", "id"),)


class Item(BaseModel, TimestampMixin, VersionMixin):
    """
    Item model - represents an item in a list.

    Example of using with_for_update() for critical operations like inventory decrement.
    """

    __tablename__ = "items"

    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_value: Mapped[float | None] = mapped_column(nullable=True)
    quantity_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    concept_id: Mapped[int | None] = mapped_column(ForeignKey("common_item_concepts.id"), nullable=True)
    is_checked: Mapped[bool] = mapped_column(default=False, nullable=False)
    checked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    price_estimate: Mapped[float | None] = mapped_column(nullable=True)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)  # HIGH, MEDIUM, LOW
    added_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optimistic locking
    version_id: Mapped[int] = mapped_column(nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version_id}
    __table_args__ = (Index("ix_items_list_id_id", "list_id", "id"),)

    # Relationships
    list: Mapped["List"] = relationship("List", back_populates="items")
