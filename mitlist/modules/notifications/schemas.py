"""Notifications module Pydantic schemas for request/response models."""

from datetime import datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ====================
# NotificationPreference Schemas
# ====================
class NotificationPreferenceBase(BaseModel):
    """Base notification preference schema."""

    event_type: str = Field(..., max_length=100)
    channel: str = Field(..., pattern="^(EMAIL|PUSH|SMS|IN_APP)$")
    enabled: bool = True
    advance_notice_hours: Optional[int] = Field(None, ge=0)
    quiet_hours_start: Optional[time] = None


class NotificationPreferenceCreate(NotificationPreferenceBase):
    """Schema for creating a notification preference."""

    pass  # user_id comes from auth context


class NotificationPreferenceUpdate(BaseModel):
    """Schema for updating a notification preference."""

    enabled: Optional[bool] = None
    advance_notice_hours: Optional[int] = Field(None, ge=0)
    quiet_hours_start: Optional[time] = None


class NotificationPreferenceResponse(NotificationPreferenceBase):
    """Schema for notification preference response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class BulkNotificationPreferenceUpdate(BaseModel):
    """Schema for bulk updating notification preferences."""

    preferences: list[NotificationPreferenceCreate]


# ====================
# Notification Schemas
# ====================
class NotificationBase(BaseModel):
    """Base notification schema."""

    type: str = Field(..., max_length=100)
    title: str = Field(..., min_length=1, max_length=255)
    body: str = Field(..., min_length=1)
    link_url: Optional[str] = Field(None, max_length=500)
    priority: str = Field("MEDIUM", pattern="^(LOW|MEDIUM|HIGH)$")


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""

    user_id: int
    group_id: Optional[int] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    group_id: Optional[int] = None
    is_read: bool
    read_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class NotificationMarkReadRequest(BaseModel):
    """Schema for marking notifications as read."""

    notification_ids: list[int] = Field(..., min_length=1)


class NotificationMarkAllReadRequest(BaseModel):
    """Schema for marking all notifications as read."""

    group_id: Optional[int] = None  # If provided, only marks notifications for this group


# ====================
# Comment Schemas
# ====================
class CommentBase(BaseModel):
    """Base comment schema."""

    parent_type: str = Field(
        ...,
        pattern="^(EXPENSE|CHORE|PROPOSAL|PET|PLANT|ASSET|RECIPE)$",
    )
    parent_id: int
    content: str = Field(..., min_length=1)


class CommentCreate(CommentBase):
    """Schema for creating a comment."""

    mentioned_user_ids: list[int] = Field(default_factory=list)


class CommentUpdate(BaseModel):
    """Schema for updating a comment."""

    content: str = Field(..., min_length=1)


class MentionResponse(BaseModel):
    """Schema for mention response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    comment_id: int
    mentioned_user_id: int
    is_read: bool
    created_at: datetime
    updated_at: datetime


class CommentResponse(CommentBase):
    """Schema for comment response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    is_edited: bool
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    mentions: list[MentionResponse] = Field(default_factory=list)


class CommentWithReactionsResponse(CommentResponse):
    """Schema for comment with reactions."""

    reactions: list["ReactionResponse"] = Field(default_factory=list)
    reaction_counts: dict[str, int] = Field(default_factory=dict)


# ====================
# Reaction Schemas
# ====================
class ReactionBase(BaseModel):
    """Base reaction schema."""

    target_type: str = Field(..., pattern="^(COMMENT|EXPENSE|CHORE_ASSIGNMENT)$")
    target_id: int
    emoji_code: str = Field(..., min_length=1, max_length=20)


class ReactionCreate(ReactionBase):
    """Schema for creating a reaction."""

    pass  # user_id comes from auth context


class ReactionResponse(ReactionBase):
    """Schema for reaction response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    comment_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class ReactionToggleRequest(BaseModel):
    """Schema for toggling a reaction (add if not exists, remove if exists)."""

    target_type: str = Field(..., pattern="^(COMMENT|EXPENSE|CHORE_ASSIGNMENT)$")
    target_id: int
    emoji_code: str = Field(..., min_length=1, max_length=20)


class ReactionToggleResponse(BaseModel):
    """Schema for reaction toggle response."""

    action: str  # "added" or "removed"
    reaction: Optional[ReactionResponse] = None


# ====================
# Mention Schemas
# ====================
class MentionMarkReadRequest(BaseModel):
    """Schema for marking mentions as read."""

    mention_ids: list[int] = Field(..., min_length=1)


# ====================
# Aggregation/Summary Schemas
# ====================
class NotificationSummaryResponse(BaseModel):
    """Schema for notification summary."""

    user_id: int
    total_unread: int
    unread_by_type: dict[str, int]
    unread_by_priority: dict[str, int]
    oldest_unread_at: Optional[datetime] = None


class UserMentionsSummaryResponse(BaseModel):
    """Schema for user mentions summary."""

    user_id: int
    total_unread_mentions: int
    mentions_by_parent_type: dict[str, int]
    recent_mentions: list[MentionResponse]


class CommentThreadResponse(BaseModel):
    """Schema for comment thread on an entity."""

    parent_type: str
    parent_id: int
    comments: list[CommentWithReactionsResponse]
    total_comments: int
    participants: list[int]  # User IDs


class NotificationListResponse(BaseModel):
    """Schema for paginated notification list."""

    notifications: list[NotificationResponse]
    total_count: int
    unread_count: int
    has_more: bool


# Update forward reference
CommentWithReactionsResponse.model_rebuild()
