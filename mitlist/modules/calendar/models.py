"""Calendar module ORM models."""

from datetime import datetime, time
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mitlist.db.base import Base, BaseModel, TimestampMixin


class EventCategory(str):
    """Event categories."""

    BIRTHDAY = "BIRTHDAY"
    LEASE = "LEASE"
    MAINTENANCE = "MAINTENANCE"
    SOCIAL = "SOCIAL"
    HOLIDAY = "HOLIDAY"
    OTHER = "OTHER"


class RSVPStatus(str):
    """RSVP status."""

    YES = "YES"
    NO = "NO"
    MAYBE = "MAYBE"
    PENDING = "PENDING"


class CalendarEvent(BaseModel, TimestampMixin):
    """Calendar event - scheduled event."""

    __tablename__ = "calendar_events"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    event_date: Mapped[datetime] = mapped_column(nullable=False)
    event_time: Mapped[Optional[time]] = mapped_column(nullable=True)
    end_time: Mapped[Optional[time]] = mapped_column(nullable=True)
    is_all_day: Mapped[bool] = mapped_column(default=False, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )  # RRULE string
    reminder_minutes_before: Mapped[Optional[int]] = mapped_column(nullable=True)
    location_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    linked_user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )  # for birthdays
    linked_asset_id: Mapped[Optional[int]] = mapped_column(nullable=True)  # FK to home_assets
    linked_pet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("pets.id"), nullable=True
    )  # for vet appointments
    is_cancelled: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    attendees: Mapped[list["EventAttendee"]] = relationship(
        "EventAttendee", back_populates="event", cascade="all, delete-orphan"
    )


class EventAttendee(BaseModel, TimestampMixin):
    """Event attendee - RSVP tracking."""

    __tablename__ = "event_attendees"

    event_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_events.id"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rsvp_status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    rsvp_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Relationships
    event: Mapped["CalendarEvent"] = relationship("CalendarEvent", back_populates="attendees")


class Reminder(BaseModel, TimestampMixin):
    """Reminder - general purpose reminder."""

    __tablename__ = "reminders"

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    due_date: Mapped[datetime] = mapped_column(nullable=False)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
