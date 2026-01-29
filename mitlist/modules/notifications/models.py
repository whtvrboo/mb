"""Notifications module ORM models."""

from datetime import datetime, time
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import Base, BaseModel, TimestampMixin


class NotificationChannel(str):
    """Notification channels."""

    EMAIL = "EMAIL"
    PUSH = "PUSH"
    SMS = "SMS"
    IN_APP = "IN_APP"


class NotificationPriority(str):
    """Notification priorities."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ParentType(str):
    """Comment parent types."""

    EXPENSE = "EXPENSE"
    CHORE = "CHORE"
    PROPOSAL = "PROPOSAL"
    PET = "PET"
    PLANT = "PLANT"
    ASSET = "ASSET"
    RECIPE = "RECIPE"


class TargetType(str):
    """Reaction target types."""

    COMMENT = "COMMENT"
    EXPENSE = "EXPENSE"
    CHORE_ASSIGNMENT = "CHORE_ASSIGNMENT"


class NotificationPreference(BaseModel, TimestampMixin):
    """Notification preference - user notification settings."""

    __tablename__ = "notification_preferences"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    advance_notice_hours: Mapped[Optional[int]] = mapped_column(nullable=True)
    quiet_hours_start: Mapped[Optional[time]] = mapped_column(nullable=True)


class Notification(BaseModel, TimestampMixin):
    """Notification - in-app notification."""

    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("groups.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    link_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)


class Comment(BaseModel, TimestampMixin):
    """Comment - comment on any entity."""

    __tablename__ = "comments"

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    parent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int] = mapped_column(nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_edited: Mapped[bool] = mapped_column(default=False, nullable=False)
    edited_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    reactions: Mapped[list["Reaction"]] = relationship("Reaction", back_populates="comment", cascade="all, delete-orphan")
    mentions: Mapped[list["Mention"]] = relationship("Mention", back_populates="comment", cascade="all, delete-orphan")


class Reaction(BaseModel, TimestampMixin):
    """Reaction - emoji reaction."""

    __tablename__ = "reactions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False, index=True)
    emoji_code: Mapped[str] = mapped_column(String(20), nullable=False)

    # For comments specifically
    comment_id: Mapped[Optional[int]] = mapped_column(ForeignKey("comments.id"), nullable=True)

    # Relationships
    comment: Mapped[Optional["Comment"]] = relationship("Comment", back_populates="reactions")


class Mention(BaseModel, TimestampMixin):
    """Mention - @username tagging in comments."""

    __tablename__ = "mentions"

    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), nullable=False, index=True)
    mentioned_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    comment: Mapped["Comment"] = relationship("Comment", back_populates="mentions")
