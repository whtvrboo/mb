"""Notifications module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_user, get_db
from mitlist.modules.auth.models import User
from mitlist.modules.notifications import schemas
from mitlist.modules.notifications.interface import (
    create_comment,
    delete_comment,
    get_comment_by_id,
    get_unread_count,
    list_comments,
    list_notifications,
    list_reactions,
    mark_all_read,
    mark_read,
    toggle_reaction,
    update_comment,
    get_preferences,
    update_preference,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=schemas.NotificationListResponse)
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the current user."""
    notifications = await list_notifications(db, user.id, unread_only=unread_only, limit=limit, offset=offset)
    unread = await get_unread_count(db, user.id)
    
    return schemas.NotificationListResponse(
        notifications=notifications,
        total_count=len(notifications),
        unread_count=unread,
        has_more=len(notifications) == limit,
    )


@router.patch("/{notification_id}/read", response_model=schemas.NotificationResponse)
async def patch_notification_read(
    notification_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    notification = await mark_read(db, notification_id, user.id)
    return notification


@router.post("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def post_notifications_clear(
    data: schemas.NotificationMarkAllReadRequest = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    group_id = data.group_id if data else None
    await mark_all_read(db, user.id, group_id)


@router.get("/count", response_model=dict)
async def get_notifications_count(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get unread notification count."""
    count = await get_unread_count(db, user.id)
    return {"unread_count": count}


@router.get("/preferences", response_model=ListType[schemas.NotificationPreferenceResponse])
async def get_notification_preferences(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get notification preferences for the current user."""
    preferences = await get_preferences(db, user.id)
    return preferences


@router.patch("/preferences", response_model=schemas.NotificationPreferenceResponse)
async def patch_notification_preference(
    data: schemas.NotificationPreferenceCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update or create a notification preference."""
    pref = await update_preference(
        db,
        user.id,
        data.event_type,
        data.channel,
        enabled=data.enabled,
        advance_notice_hours=data.advance_notice_hours,
    )
    return pref


# ---------- Comments ----------
comments_router = APIRouter(prefix="/comments", tags=["comments"])


@comments_router.get("", response_model=ListType[schemas.CommentWithReactionsResponse])
async def get_comments_list(
    parent_type: str,
    parent_id: int,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List comments for an entity."""
    comments = await list_comments(db, parent_type, parent_id, limit=limit, offset=offset)
    
    # Build response with reaction counts
    result = []
    for comment in comments:
        reaction_counts: dict[str, int] = {}
        for reaction in comment.reactions:
            reaction_counts[reaction.emoji_code] = reaction_counts.get(reaction.emoji_code, 0) + 1
        
        result.append(
            schemas.CommentWithReactionsResponse(
                id=comment.id,
                author_id=comment.author_id,
                parent_type=comment.parent_type,
                parent_id=comment.parent_id,
                content=comment.content,
                is_edited=comment.is_edited,
                edited_at=comment.edited_at,
                deleted_at=comment.deleted_at,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
                mentions=[
                    schemas.MentionResponse(
                        id=m.id,
                        comment_id=m.comment_id,
                        mentioned_user_id=m.mentioned_user_id,
                        is_read=m.is_read,
                        created_at=m.created_at,
                        updated_at=m.updated_at,
                    )
                    for m in comment.mentions
                ],
                reactions=[
                    schemas.ReactionResponse(
                        id=r.id,
                        user_id=r.user_id,
                        target_type=r.target_type,
                        target_id=r.target_id,
                        emoji_code=r.emoji_code,
                        comment_id=r.comment_id,
                        created_at=r.created_at,
                        updated_at=r.updated_at,
                    )
                    for r in comment.reactions
                ],
                reaction_counts=reaction_counts,
            )
        )
    return result


@comments_router.post("", response_model=schemas.CommentResponse, status_code=status.HTTP_201_CREATED)
async def post_comment(
    data: schemas.CommentCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a comment."""
    comment = await create_comment(
        db,
        author_id=user.id,
        parent_type=data.parent_type,
        parent_id=data.parent_id,
        content=data.content,
        mentioned_user_ids=data.mentioned_user_ids,
    )
    comment = await get_comment_by_id(db, comment.id)
    return schemas.CommentResponse.model_validate(comment)


@comments_router.patch("/{comment_id}", response_model=schemas.CommentResponse)
async def patch_comment(
    comment_id: int,
    data: schemas.CommentUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a comment."""
    await update_comment(db, comment_id, user.id, data.content)
    comment = await get_comment_by_id(db, comment_id)
    return schemas.CommentResponse.model_validate(comment)


@comments_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_endpoint(
    comment_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a comment."""
    await delete_comment(db, comment_id, user.id)


# ---------- Reactions ----------
reactions_router = APIRouter(prefix="/reactions", tags=["reactions"])


@reactions_router.post("/toggle", response_model=schemas.ReactionToggleResponse)
async def post_reaction_toggle(
    data: schemas.ReactionToggleRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle a reaction (add if not exists, remove if exists)."""
    action, reaction = await toggle_reaction(
        db, user.id, data.target_type, data.target_id, data.emoji_code
    )
    reaction_response = None
    if reaction:
        reaction_response = schemas.ReactionResponse(
            id=reaction.id,
            user_id=reaction.user_id,
            target_type=reaction.target_type,
            target_id=reaction.target_id,
            emoji_code=reaction.emoji_code,
            comment_id=reaction.comment_id,
            created_at=reaction.created_at,
            updated_at=reaction.updated_at,
        )
    return schemas.ReactionToggleResponse(action=action, reaction=reaction_response)


@reactions_router.get("", response_model=ListType[schemas.ReactionResponse])
async def get_reactions_list(
    target_type: str,
    target_id: int,
    db: AsyncSession = Depends(get_db),
):
    """List reactions for a target."""
    reactions = await list_reactions(db, target_type, target_id)
    return reactions
