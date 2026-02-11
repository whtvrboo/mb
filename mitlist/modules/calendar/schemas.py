"""Calendar module Pydantic schemas for request/response models."""

from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field


# ====================
# CalendarEvent Schemas
# ====================
class CalendarEventBase(BaseModel):
    """Base calendar event schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    event_date: datetime
    event_time: time | None = None
    end_time: time | None = None
    is_all_day: bool = False
    category: str = Field(
        ...,
        pattern="^(BIRTHDAY|LEASE|MAINTENANCE|SOCIAL|HOLIDAY|OTHER)$",
    )
    recurrence_rule: str | None = Field(None, max_length=500)  # RRULE string
    reminder_minutes_before: int | None = Field(None, ge=0)
    location_text: str | None = Field(None, max_length=500)


class CalendarEventCreate(CalendarEventBase):
    """Schema for creating a calendar event."""

    group_id: int
    linked_user_id: int | None = None  # For birthdays
    linked_asset_id: int | None = None  # For maintenance
    linked_pet_id: int | None = None  # For vet appointments
    attendee_ids: list[int] = Field(default_factory=list)


class CalendarEventUpdate(BaseModel):
    """Schema for updating a calendar event."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    event_date: datetime | None = None
    event_time: time | None = None
    end_time: time | None = None
    is_all_day: bool | None = None
    category: str | None = Field(
        None,
        pattern="^(BIRTHDAY|LEASE|MAINTENANCE|SOCIAL|HOLIDAY|OTHER)$",
    )
    recurrence_rule: str | None = Field(None, max_length=500)
    reminder_minutes_before: int | None = Field(None, ge=0)
    location_text: str | None = Field(None, max_length=500)
    linked_user_id: int | None = None
    linked_asset_id: int | None = None
    linked_pet_id: int | None = None


class CalendarEventCancelRequest(BaseModel):
    """Schema for cancelling an event."""

    notify_attendees: bool = True


class EventAttendeeResponse(BaseModel):
    """Schema for event attendee response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    event_id: int
    user_id: int
    rsvp_status: str
    rsvp_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class CalendarEventResponse(CalendarEventBase):
    """Schema for calendar event response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    created_by_id: int
    linked_user_id: int | None = None
    linked_asset_id: int | None = None
    linked_pet_id: int | None = None
    is_cancelled: bool
    created_at: datetime
    updated_at: datetime
    attendees: list[EventAttendeeResponse] = Field(default_factory=list)


# ====================
# EventAttendee Schemas
# ====================
class EventAttendeeCreate(BaseModel):
    """Schema for adding an attendee to an event."""

    event_id: int
    user_id: int


class RSVPRequest(BaseModel):
    """Schema for RSVP to an event."""

    rsvp_status: str = Field(..., pattern="^(YES|NO|MAYBE|PENDING)$")


class RSVPResponse(BaseModel):
    """Schema for RSVP response."""

    event_id: int
    user_id: int
    rsvp_status: str
    rsvp_at: datetime


# ====================
# Reminder Schemas
# ====================
class ReminderBase(BaseModel):
    """Base reminder schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime
    priority: str | None = Field(None, pattern="^(LOW|MEDIUM|HIGH)$")


class ReminderCreate(ReminderBase):
    """Schema for creating a reminder."""

    group_id: int


class ReminderUpdate(BaseModel):
    """Schema for updating a reminder."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    due_date: datetime | None = None
    priority: str | None = Field(None, pattern="^(LOW|MEDIUM|HIGH)$")


class ReminderCompleteRequest(BaseModel):
    """Schema for completing a reminder."""

    pass  # No input needed


class ReminderResponse(ReminderBase):
    """Schema for reminder response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    group_id: int
    user_id: int
    is_completed: bool
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


# ====================
# Aggregation/Summary Schemas
# ====================
class CalendarRangeRequest(BaseModel):
    """Schema for requesting events in a date range."""

    group_id: int
    start_date: datetime
    end_date: datetime
    categories: list[str] | None = None
    include_cancelled: bool = False


class CalendarDayResponse(BaseModel):
    """Schema for a single day's events."""

    date: datetime
    events: list[CalendarEventResponse]
    reminders: list[ReminderResponse]
    event_count: int
    reminder_count: int


class CalendarMonthResponse(BaseModel):
    """Schema for a month's calendar view."""

    group_id: int
    year: int
    month: int
    days: list[CalendarDayResponse]
    total_events: int
    total_reminders: int


class UpcomingEventsResponse(BaseModel):
    """Schema for upcoming events."""

    group_id: int
    events: list[CalendarEventResponse]
    days_ahead: int
    total_count: int


class BirthdayListResponse(BaseModel):
    """Schema for birthday list."""

    group_id: int
    upcoming_birthdays: list[dict]  # user_id, name, birth_date, days_until
    this_month: list[dict]
    total_count: int


class EventReminderDueResponse(BaseModel):
    """Schema for event reminder due notification."""

    event: CalendarEventResponse
    reminder_minutes_before: int
    event_starts_at: datetime
    reminder_sent_at: datetime


class RecurringEventInstancesRequest(BaseModel):
    """Schema for requesting recurring event instances."""

    event_id: int
    start_date: datetime
    end_date: datetime
    max_instances: int = Field(50, ge=1, le=100)


class RecurringEventInstancesResponse(BaseModel):
    """Schema for recurring event instances."""

    event_id: int
    instances: list[datetime]
    total_instances: int
    recurrence_rule: str


class GroupCalendarSummaryResponse(BaseModel):
    """Schema for group calendar summary."""

    group_id: int
    events_this_week: int
    events_this_month: int
    upcoming_birthdays: int
    overdue_reminders: int
    next_event: CalendarEventResponse | None = None
