"""Gamification module service layer. PRIVATE - other modules import from interface.py."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from mitlist.core.errors import NotFoundError
from mitlist.modules.gamification.models import (
    Achievement,
    Leaderboard,
    Streak,
    UserAchievement,
    UserPoints,
)


# ---------- Points ----------
async def get_user_points(db: AsyncSession, user_id: int, group_id: int) -> Optional[UserPoints]:
    """Get user points for a group."""
    result = await db.execute(
        select(UserPoints).where(
            UserPoints.user_id == user_id,
            UserPoints.group_id == group_id,
        )
    )
    return result.scalar_one_or_none()


async def get_or_create_user_points(db: AsyncSession, user_id: int, group_id: int) -> UserPoints:
    """Get or create user points record."""
    points = await get_user_points(db, user_id, group_id)
    if not points:
        points = UserPoints(
            user_id=user_id,
            group_id=group_id,
            total_points=0,
            monthly_points=0,
        )
        db.add(points)
        await db.flush()
        await db.refresh(points)
    return points


async def award_points(
    db: AsyncSession,
    user_id: int,
    group_id: int,
    points: int,
    reason: str,
) -> UserPoints:
    """Award points to a user."""
    user_points = await get_or_create_user_points(db, user_id, group_id)
    user_points.total_points += points
    user_points.monthly_points += points
    await db.flush()
    await db.refresh(user_points)
    return user_points


async def reset_monthly_points(db: AsyncSession, group_id: int) -> int:
    """Reset monthly points for all users in a group. Returns count reset."""
    from sqlalchemy import update

    result = await db.execute(
        update(UserPoints)
        .where(UserPoints.group_id == group_id)
        .values(monthly_points=0, last_reset_at=datetime.now(timezone.utc))
    )
    await db.flush()
    return result.rowcount


# ---------- Achievements ----------
async def list_achievements(db: AsyncSession, category: Optional[str] = None) -> list[Achievement]:
    """List all achievements, optionally filtered by category."""
    q = select(Achievement).where(Achievement.is_active == True)  # noqa: E712
    if category:
        q = q.where(Achievement.category == category)
    q = q.order_by(Achievement.requirement_value.asc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_achievement_by_id(db: AsyncSession, achievement_id: int) -> Optional[Achievement]:
    """Get achievement by ID."""
    result = await db.execute(
        select(Achievement).where(Achievement.id == achievement_id)
    )
    return result.scalar_one_or_none()


async def get_user_achievements(db: AsyncSession, user_id: int) -> list[UserAchievement]:
    """Get user's earned achievements."""
    result = await db.execute(
        select(UserAchievement)
        .where(UserAchievement.user_id == user_id)
        .options(selectinload(UserAchievement.achievement))
        .order_by(UserAchievement.earned_at.desc())
    )
    return list(result.scalars().all())


async def award_achievement(
    db: AsyncSession,
    user_id: int,
    achievement_id: int,
) -> UserAchievement:
    """Award an achievement to a user."""
    # Check if already earned
    result = await db.execute(
        select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    user_achievement = UserAchievement(
        user_id=user_id,
        achievement_id=achievement_id,
        earned_at=datetime.now(timezone.utc),
        progress_percentage=100,
    )
    db.add(user_achievement)
    await db.flush()
    await db.refresh(user_achievement)
    return user_achievement


async def _get_activity_count_for_category(
    db: AsyncSession,
    user_id: int,
    group_id: int,
    category: str,
) -> int:
    """Return count of user activities in the given category (for COUNT achievements)."""
    if category == "CHORES":
        from mitlist.modules.chores.models import Chore, ChoreAssignment

        result = await db.execute(
            select(func.count(ChoreAssignment.id))
            .select_from(ChoreAssignment)
            .join(Chore, ChoreAssignment.chore_id == Chore.id)
            .where(
                Chore.group_id == group_id,
                ChoreAssignment.assigned_to_id == user_id,
                ChoreAssignment.status == "COMPLETED",
            )
        )
        return result.scalar() or 0
    if category == "FINANCE":
        from mitlist.modules.finance.models import Expense

        result = await db.execute(
            select(func.count(Expense.id)).where(
                Expense.group_id == group_id,
                Expense.paid_by_user_id == user_id,
            )
        )
        return result.scalar() or 0
    # PLANTS / PETS: no user-scoped activity count in this codebase yet
    return 0


async def check_and_award_achievements(
    db: AsyncSession,
    user_id: int,
    group_id: int,
) -> list[Achievement]:
    """Check if user qualifies for any new achievements and award them."""
    # Get user's current points
    user_points = await get_user_points(db, user_id, group_id)
    if not user_points:
        return []

    # Get user's current streaks
    streaks = await get_user_streaks(db, user_id, group_id)
    max_streak = max((s.current_streak_days for s in streaks), default=0)

    # Get already earned achievement IDs
    earned_result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
    )
    earned_ids = set(earned_result.scalars().all())

    # Get all achievements
    all_achievements = await list_achievements(db)

    newly_awarded = []
    for achievement in all_achievements:
        if achievement.id in earned_ids:
            continue

        # Check if user qualifies
        qualifies = False
        if achievement.requirement_type == "POINTS":
            qualifies = user_points.total_points >= achievement.requirement_value
        elif achievement.requirement_type == "STREAK":
            qualifies = max_streak >= achievement.requirement_value
        elif achievement.requirement_type == "COUNT":
            count = await _get_activity_count_for_category(
                db, user_id, group_id, achievement.category
            )
            qualifies = count >= achievement.requirement_value

        if qualifies:
            await award_achievement(db, user_id, achievement.id)
            newly_awarded.append(achievement)

    return newly_awarded


# ---------- Streaks ----------
async def get_user_streaks(db: AsyncSession, user_id: int, group_id: int) -> list[Streak]:
    """Get user's streaks for a group."""
    result = await db.execute(
        select(Streak).where(
            Streak.user_id == user_id,
            Streak.group_id == group_id,
        )
    )
    return list(result.scalars().all())


async def get_streak(
    db: AsyncSession,
    user_id: int,
    group_id: int,
    activity_type: str,
) -> Optional[Streak]:
    """Get a specific streak."""
    result = await db.execute(
        select(Streak).where(
            Streak.user_id == user_id,
            Streak.group_id == group_id,
            Streak.activity_type == activity_type,
        )
    )
    return result.scalar_one_or_none()


async def record_activity(
    db: AsyncSession,
    user_id: int,
    group_id: int,
    activity_type: str,
) -> tuple[Streak, bool, bool]:
    """Record activity for streak tracking. Returns (streak, extended, is_new_record)."""
    streak = await get_streak(db, user_id, group_id, activity_type)
    today = datetime.now(timezone.utc).date()

    if not streak:
        # Create new streak
        streak = Streak(
            user_id=user_id,
            group_id=group_id,
            activity_type=activity_type,
            current_streak_days=1,
            longest_streak_days=1,
            last_activity_date=datetime.now(timezone.utc),
        )
        db.add(streak)
        await db.flush()
        await db.refresh(streak)
        return streak, True, True

    # Check if activity was already recorded today
    if streak.last_activity_date and streak.last_activity_date.date() == today:
        return streak, False, False

    # Check if streak continues (activity yesterday)
    yesterday = today - timedelta(days=1)
    extended = False
    is_new_record = False

    if streak.last_activity_date and streak.last_activity_date.date() == yesterday:
        # Streak continues
        streak.current_streak_days += 1
        extended = True
        if streak.current_streak_days > streak.longest_streak_days:
            streak.longest_streak_days = streak.current_streak_days
            is_new_record = True
    else:
        # Streak broken, reset to 1
        streak.current_streak_days = 1
        extended = True  # New streak started

    streak.last_activity_date = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(streak)
    return streak, extended, is_new_record


# ---------- Leaderboard ----------
async def get_leaderboard(
    db: AsyncSession,
    group_id: int,
    period_type: str = "MONTHLY",
    metric: str = "POINTS",
) -> list[dict]:
    """Get leaderboard entries for a group."""
    from mitlist.modules.auth.models import User

    # Rank by user points
    if metric == "POINTS":
        if period_type == "MONTHLY":
            order_col = UserPoints.monthly_points
        else:
            order_col = UserPoints.total_points

        result = await db.execute(
            select(UserPoints, User.name, User.avatar_url)
            .join(User, User.id == UserPoints.user_id)
            .where(UserPoints.group_id == group_id)
            .order_by(order_col.desc())
            .limit(50)
        )
        rows = result.all()

        entries = []
        for idx, (points, name, avatar_url) in enumerate(rows, start=1):
            entries.append({
                "rank": idx,
                "user_id": points.user_id,
                "user_name": name,
                "avatar_url": avatar_url,
                "value": points.monthly_points if period_type == "MONTHLY" else points.total_points,
                "change_from_previous": None,
            })
        return entries

    return []


async def get_user_gamification_summary(
    db: AsyncSession,
    user_id: int,
    group_id: int,
) -> dict:
    """Get gamification summary for a user."""
    user_points = await get_or_create_user_points(db, user_id, group_id)
    achievements = await get_user_achievements(db, user_id)
    all_achievements = await list_achievements(db)
    streaks = await get_user_streaks(db, user_id, group_id)
    longest_streak_ever = max((s.longest_streak_days for s in streaks), default=0)

    return {
        "user_id": user_id,
        "group_id": group_id,
        "total_points": user_points.total_points,
        "monthly_points": user_points.monthly_points,
        "rank_position": user_points.rank_position,
        "achievements_earned": len(achievements),
        "total_achievements": len(all_achievements),
        "active_streaks": streaks,
        "longest_streak_ever": longest_streak_ever,
        "recent_achievements": achievements[:5],
    }
