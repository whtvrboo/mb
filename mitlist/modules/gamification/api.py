"""Gamification & Social module FastAPI router."""

from typing import List as ListType

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.api.deps import get_current_group_id, get_current_user, get_db, require_group_admin
from mitlist.modules.auth.models import User
from mitlist.modules.gamification import schemas
from mitlist.modules.gamification.interface import (
    award_points,
    check_and_award_achievements,
    get_leaderboard,
    get_user_achievements,
    get_user_gamification_summary,
    get_user_points,
    get_user_streaks,
    list_achievements,
    record_activity,
)

router = APIRouter(prefix="/gamification", tags=["gamification"])


@router.get("/points", response_model=schemas.UserPointsResponse)
async def get_points(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's points for the group."""
    from mitlist.modules.gamification.interface import get_or_create_user_points

    points = await get_or_create_user_points(db, user.id, group_id)
    return points


@router.post("/points/award", response_model=schemas.AwardPointsResponse)
async def post_award_points(
    data: schemas.AwardPointsRequest,
    _admin: int = Depends(require_group_admin),
    db: AsyncSession = Depends(get_db),
):
    """Award points to a user (admin only)."""
    points = await award_points(db, data.user_id, data.group_id, data.points, data.reason)
    return schemas.AwardPointsResponse(
        user_id=data.user_id,
        points_awarded=data.points,
        new_total=points.total_points,
        new_monthly=points.monthly_points,
        reason=data.reason,
    )


@router.get("/achievements", response_model=ListType[schemas.AchievementResponse])
async def get_all_achievements(
    category: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """List all available achievements."""
    achievements = await list_achievements(db, category=category)
    return achievements


@router.get("/achievements/me", response_model=ListType[schemas.UserAchievementWithDetailsResponse])
async def get_my_achievements(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's earned achievements."""
    achievements = await get_user_achievements(db, user.id)
    return achievements


@router.post("/achievements/check", response_model=ListType[schemas.AchievementResponse])
async def post_check_achievements(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Check and award any new achievements for the current user."""
    newly_awarded = await check_and_award_achievements(db, user.id, group_id)
    return newly_awarded


@router.get("/streaks", response_model=ListType[schemas.StreakResponse])
async def get_streaks(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's streaks."""
    streaks = await get_user_streaks(db, user.id, group_id)
    return streaks


@router.post("/streaks/record", response_model=schemas.StreakRecordActivityResponse)
async def post_record_activity(
    data: schemas.StreakRecordActivityRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record activity for streak tracking."""
    streak, extended, is_new_record = await record_activity(
        db, user.id, data.group_id, data.activity_type
    )
    return schemas.StreakRecordActivityResponse(
        streak=streak,
        streak_extended=extended,
        is_new_record=is_new_record,
    )


@router.get("/leaderboard", response_model=schemas.LeaderboardWithEntriesResponse)
async def get_leaderboard_endpoint(
    period_type: str = "MONTHLY",
    metric: str = "POINTS",
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get group leaderboard."""
    from datetime import datetime

    entries = await get_leaderboard(db, group_id, period_type, metric)

    # Find current user's rank
    current_user_rank = None
    for entry in entries:
        if entry["user_id"] == user.id:
            current_user_rank = entry["rank"]
            break

    return schemas.LeaderboardWithEntriesResponse(
        id=0,  # Virtual leaderboard
        group_id=group_id,
        period_type=period_type,
        metric=metric,
        period_start_date=datetime.utcnow(),
        period_end_date=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        entries=[
            schemas.LeaderboardEntryResponse(
                rank=e["rank"],
                user_id=e["user_id"],
                user_name=e["user_name"],
                avatar_url=e["avatar_url"],
                value=e["value"],
                change_from_previous=e["change_from_previous"],
            )
            for e in entries
        ],
        total_participants=len(entries),
        current_user_rank=current_user_rank,
    )


@router.get("/summary", response_model=schemas.UserGamificationSummaryResponse)
async def get_summary(
    group_id: int = Depends(get_current_group_id),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get gamification summary for the current user."""
    summary = await get_user_gamification_summary(db, user.id, group_id)
    return summary
