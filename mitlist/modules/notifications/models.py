"""Notifications module ORM models."""

from datetime import datetime, time

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import BaseModel, TimestampMixin


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
    advance_notice_hours: Mapped[int | None] = mapped_column(nullable=True)
    quiet_hours_start: Mapped[time | None] = mapped_column(nullable=True)


class Notification(BaseModel, TimestampMixin):
    """Notification - in-app notification."""

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_lookup", "user_id", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    link_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(nullable=True)


class Comment(BaseModel, TimestampMixin):
    """Comment - comment on any entity."""

    __tablename__ = "comments"
    __table_args__ = (
        Index("ix_comments_parent_lookup", "parent_type", "parent_id", "created_at"),
    )

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    parent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    parent_id: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_edited: Mapped[bool] = mapped_column(default=False, nullable=False)
    edited_at: Mapped[datetime | None] = mapped_column(nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Relationships
    reactions: Mapped[list["Reaction"]] = relationship(
        "Reaction", back_populates="comment", cascade="all, delete-orphan"
    )
    mentions: Mapped[list["Mention"]] = relationship(
        "Mention", back_populates="comment", cascade="all, delete-orphan"
    )


class Reaction(BaseModel, TimestampMixin):
    """Reaction - emoji reaction."""

    __tablename__ = "reactions"
    __table_args__ = (
        Index("ix_reactions_target_lookup", "target_type", "target_id"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_id: Mapped[int] = mapped_column(nullable=False)
    emoji_code: Mapped[str] = mapped_column(String(20), nullable=False)

    # For comments specifically
    comment_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id"), nullable=True, index=True
    )

    # Relationships
    comment: Mapped[Comment | None] = relationship("Comment", back_populates="reactions")


class Mention(BaseModel, TimestampMixin):
    """Mention - @username tagging in comments."""

    __tablename__ = "mentions"

    comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), nullable=False, index=True)
    mentioned_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_read: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    comment: Mapped[Comment] = relationship("Comment", back_populates="mentions")
