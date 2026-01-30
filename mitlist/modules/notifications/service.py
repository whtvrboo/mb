"""Notifications module service layer. PRIVATE - other modules import from interface.py."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import ForbiddenError, NotFoundError
from mitlist.modules.notifications.models import (
    Comment,
    Mention,
    Notification,
    NotificationPreference,
    Reaction,
)


# ---------- Notifications ----------
async def list_notifications(
    db: AsyncSession,
    user_id: int,
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> list[Notification]:
    """List notifications for a user."""
    q = select(Notification).where(Notification.user_id == user_id)
    if unread_only:
        q = q.where(Notification.is_read == False)  # noqa: E712
    q = q.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(q)
    return list(result.scalars().all())


async def create_notification(
    db: AsyncSession,
    user_id: int,
    type: str,
    title: str,
    body: str,
    group_id: Optional[int] = None,
    link_url: Optional[str] = None,
    priority: str = "MEDIUM",
) -> Notification:
    """Create a notification for a user."""
    notification = Notification(
        user_id=user_id,
        group_id=group_id,
        type=type,
        title=title,
        body=body,
        link_url=link_url,
        priority=priority,
        is_read=False,
        delivered_at=datetime.now(timezone.utc),
    )
    db.add(notification)
    await db.flush()
    await db.refresh(notification)
    return notification


async def get_notification_by_id(db: AsyncSession, notification_id: int) -> Optional[Notification]:
    """Get notification by ID."""
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    return result.scalar_one_or_none()


async def mark_read(db: AsyncSession, notification_id: int, user_id: int) -> Notification:
    """Mark a notification as read."""
    notification = await get_notification_by_id(db, notification_id)
    if not notification:
        raise NotFoundError(code="NOTIFICATION_NOT_FOUND", detail=f"Notification {notification_id} not found")
    if notification.user_id != user_id:
        raise ForbiddenError(code="NOT_OWNER", detail="Cannot mark another user's notification as read")
    
    notification.is_read = True
    notification.read_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(notification)
    return notification


async def mark_all_read(db: AsyncSession, user_id: int, group_id: Optional[int] = None) -> int:
    """Mark all notifications as read for a user. Returns count marked."""
    q = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)  # noqa: E712
        .values(is_read=True, read_at=datetime.now(timezone.utc))
    )
    if group_id is not None:
        q = q.where(Notification.group_id == group_id)
    
    result = await db.execute(q)
    await db.flush()
    return result.rowcount


async def get_unread_count(db: AsyncSession, user_id: int) -> int:
    """Get unread notification count for a user."""
    result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.user_id == user_id,
            Notification.is_read == False,  # noqa: E712
        )
    )
    return result.scalar_one() or 0


# ---------- Notification Preferences ----------
async def get_preferences(db: AsyncSession, user_id: int) -> list[NotificationPreference]:
    """Get notification preferences for a user."""
    result = await db.execute(
        select(NotificationPreference).where(NotificationPreference.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_preference(
    db: AsyncSession, user_id: int, event_type: str, channel: str
) -> Optional[NotificationPreference]:
    """Get a specific notification preference."""
    result = await db.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == user_id,
            NotificationPreference.event_type == event_type,
            NotificationPreference.channel == channel,
        )
    )
    return result.scalar_one_or_none()


async def update_preference(
    db: AsyncSession,
    user_id: int,
    event_type: str,
    channel: str,
    enabled: Optional[bool] = None,
    advance_notice_hours: Optional[int] = None,
) -> NotificationPreference:
    """Update or create a notification preference."""
    pref = await get_preference(db, user_id, event_type, channel)
    
    if pref is None:
        # Create new preference
        pref = NotificationPreference(
            user_id=user_id,
            event_type=event_type,
            channel=channel,
            enabled=enabled if enabled is not None else True,
            advance_notice_hours=advance_notice_hours,
        )
        db.add(pref)
    else:
        if enabled is not None:
            pref.enabled = enabled
        if advance_notice_hours is not None:
            pref.advance_notice_hours = advance_notice_hours
    
    await db.flush()
    await db.refresh(pref)
    return pref


# ---------- Comments ----------
async def list_comments(
    db: AsyncSession,
    parent_type: str,
    parent_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[Comment]:
    """List comments for an entity."""
    result = await db.execute(
        select(Comment)
        .where(
            Comment.parent_type == parent_type,
            Comment.parent_id == parent_id,
            Comment.deleted_at.is_(None),
        )
        .options(selectinload(Comment.mentions), selectinload(Comment.reactions))
        .order_by(Comment.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_comment_by_id(db: AsyncSession, comment_id: int) -> Optional[Comment]:
    """Get comment by ID."""
    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment_id, Comment.deleted_at.is_(None))
        .options(selectinload(Comment.mentions), selectinload(Comment.reactions))
    )
    return result.scalar_one_or_none()


async def create_comment(
    db: AsyncSession,
    author_id: int,
    parent_type: str,
    parent_id: int,
    content: str,
    mentioned_user_ids: Optional[list[int]] = None,
) -> Comment:
    """Create a comment with optional mentions."""
    comment = Comment(
        author_id=author_id,
        parent_type=parent_type,
        parent_id=parent_id,
        content=content,
    )
    db.add(comment)
    await db.flush()
    
    # Create mentions
    if mentioned_user_ids:
        for user_id in mentioned_user_ids:
            mention = Mention(
                comment_id=comment.id,
                mentioned_user_id=user_id,
                is_read=False,
            )
            db.add(mention)
        await db.flush()
    
    await db.refresh(comment)
    return comment


async def update_comment(db: AsyncSession, comment_id: int, user_id: int, content: str) -> Comment:
    """Update a comment (only author can update)."""
    comment = await get_comment_by_id(db, comment_id)
    if not comment:
        raise NotFoundError(code="COMMENT_NOT_FOUND", detail=f"Comment {comment_id} not found")
    if comment.author_id != user_id:
        raise ForbiddenError(code="NOT_AUTHOR", detail="Only the author can edit this comment")
    
    comment.content = content
    comment.is_edited = True
    comment.edited_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment_id: int, user_id: int) -> None:
    """Soft delete a comment (only author can delete)."""
    comment = await get_comment_by_id(db, comment_id)
    if not comment:
        raise NotFoundError(code="COMMENT_NOT_FOUND", detail=f"Comment {comment_id} not found")
    if comment.author_id != user_id:
        raise ForbiddenError(code="NOT_AUTHOR", detail="Only the author can delete this comment")
    
    comment.deleted_at = datetime.now(timezone.utc)
    await db.flush()


# ---------- Reactions ----------
async def get_reaction(
    db: AsyncSession,
    user_id: int,
    target_type: str,
    target_id: int,
    emoji_code: str,
) -> Optional[Reaction]:
    """Get a specific reaction."""
    result = await db.execute(
        select(Reaction).where(
            Reaction.user_id == user_id,
            Reaction.target_type == target_type,
            Reaction.target_id == target_id,
            Reaction.emoji_code == emoji_code,
        )
    )
    return result.scalar_one_or_none()


async def toggle_reaction(
    db: AsyncSession,
    user_id: int,
    target_type: str,
    target_id: int,
    emoji_code: str,
) -> tuple[str, Optional[Reaction]]:
    """Toggle a reaction (add if not exists, remove if exists). Returns (action, reaction)."""
    existing = await get_reaction(db, user_id, target_type, target_id, emoji_code)
    
    if existing:
        await db.delete(existing)
        await db.flush()
        return ("removed", None)
    
    # Create new reaction
    comment_id = target_id if target_type == "COMMENT" else None
    reaction = Reaction(
        user_id=user_id,
        target_type=target_type,
        target_id=target_id,
        emoji_code=emoji_code,
        comment_id=comment_id,
    )
    db.add(reaction)
    await db.flush()
    await db.refresh(reaction)
    return ("added", reaction)


async def list_reactions(
    db: AsyncSession,
    target_type: str,
    target_id: int,
) -> list[Reaction]:
    """List reactions for a target."""
    result = await db.execute(
        select(Reaction).where(
            Reaction.target_type == target_type,
            Reaction.target_id == target_id,
        )
    )
    return list(result.scalars().all())
