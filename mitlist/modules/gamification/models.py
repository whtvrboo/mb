"""Gamification module ORM models."""

from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import BaseModel, TimestampMixin


class AchievementCategory(str):
    """Achievement categories."""

    CHORES = "CHORES"
    FINANCE = "FINANCE"
    PLANTS = "PLANTS"
    PETS = "PETS"


class RequirementType(str):
    """Requirement types."""

    POINTS = "POINTS"
    COUNT = "COUNT"
    STREAK = "STREAK"


class ActivityType(str):
    """Activity types for streaks."""

    CHORES = "CHORES"
    PLANT_CARE = "PLANT_CARE"
    PET_CARE = "PET_CARE"


class Metric(str):
    """Leaderboard metrics."""

    POINTS = "POINTS"
    CHORES_COMPLETED = "CHORES_COMPLETED"
    EXPENSES_ADDED = "EXPENSES_ADDED"


class PeriodType(str):
    """Period types."""

    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    ALL_TIME = "ALL_TIME"


class UserPoints(BaseModel, TimestampMixin):
    """User points - points tracking per group."""

    __tablename__ = "user_points"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    total_points: Mapped[int] = mapped_column(default=0, nullable=False)
    monthly_points: Mapped[int] = mapped_column(default=0, nullable=False)
    last_reset_at: Mapped[datetime | None] = mapped_column(nullable=True)
    rank_position: Mapped[int | None] = mapped_column(nullable=True)

    __table_args__ = (
        CheckConstraint("total_points >= 0", name="ck_user_points_total_non_negative"),
        CheckConstraint("monthly_points >= 0", name="ck_user_points_monthly_non_negative"),
    )


class Achievement(BaseModel, TimestampMixin):
    """Achievement - achievement definition."""

    __tablename__ = "achievements"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    badge_icon_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    requirement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    requirement_value: Mapped[int] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement", back_populates="achievement", cascade="all, delete-orphan"
    )


class UserAchievement(BaseModel, TimestampMixin):
    """User achievement - earned achievement."""

    __tablename__ = "user_achievements"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    achievement_id: Mapped[int] = mapped_column(ForeignKey("achievements.id"), nullable=False)
    earned_at: Mapped[datetime] = mapped_column(nullable=False)
    progress_percentage: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relationships
    achievement: Mapped["Achievement"] = relationship(
        "Achievement", back_populates="user_achievements"
    )

    __table_args__ = (
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="ck_user_achievement_progress",
        ),
    )


class Streak(BaseModel, TimestampMixin):
    """Streak - activity streak tracking."""

    __tablename__ = "streaks"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    current_streak_days: Mapped[int] = mapped_column(default=0, nullable=False)
    longest_streak_days: Mapped[int] = mapped_column(default=0, nullable=False)
    last_activity_date: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        CheckConstraint("current_streak_days >= 0", name="ck_streak_current_non_negative"),
        CheckConstraint("longest_streak_days >= 0", name="ck_streak_longest_non_negative"),
    )


class Leaderboard(BaseModel, TimestampMixin):
    """Leaderboard - pre-computed leaderboard snapshots."""

    __tablename__ = "leaderboards"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(String(20), nullable=False)
    metric: Mapped[str] = mapped_column(String(50), nullable=False)
    period_start_date: Mapped[datetime] = mapped_column(nullable=False)
    period_end_date: Mapped[datetime | None] = mapped_column(nullable=True)
