---
name: Calendar Module Implementation
overview: Implement unified calendar feed that aggregates events from finance (bills), chores (deadlines), pets (vaccines), plants (care schedules), assets (maintenance), and native calendar events.
todos:
  - id: event-crud
    content: Implement CalendarEvent CRUD service functions
    status: pending
  - id: reminder-crud
    content: Implement Reminder CRUD service functions
    status: pending
  - id: feed-aggregation
    content: Implement unified feed aggregation from all source modules
    status: pending
  - id: api-endpoints
    content: Wire all endpoints (feed, events, reminders, RSVP)
    status: pending
isProject: false
---

# Calendar Module Implementation

## Current State

**Models exist** in `[mitlist/modules/calendar/models.py](mitlist/modules/calendar/models.py)`:

- `CalendarEvent` - native calendar events with recurrence
- `EventAttendee` - RSVP tracking
- `Reminder` - general reminders

**Schemas exist** in `[mitlist/modules/calendar/schemas.py](mitlist/modules/calendar/schemas.py)`

**API endpoint** (stub) in `[mitlist/modules/calendar/api.py](mitlist/modules/calendar/api.py)`:

- `GET /calendar/feed` - Unified calendar feed (501 stub)

**Service layer**: Empty

---

## Aggregation Sources

The unified feed must aggregate from:

| Module   | Source                           | Event Type      |
| -------- | -------------------------------- | --------------- |
| Finance  | `RecurringExpense.next_due_date` | Bill due        |
| Chores   | `ChoreAssignment.due_date`       | Chore deadline  |
| Pets     | `PetMedicalRecord.expires_at`    | Vaccine expiry  |
| Pets     | `Pet.date_of_birth`              | Pet birthday    |
| Plants   | `PlantSchedule.next_due_date`    | Plant care due  |
| Assets   | `MaintenanceTask.next_due_date`  | Maintenance due |
| Assets   | `HomeAsset.warranty_end_date`    | Warranty expiry |
| Auth     | `User.birth_date`                | User birthday   |
| Calendar | `CalendarEvent`                  | Native events   |
| Calendar | `Reminder.due_date`              | Reminders       |

---

## Implementation Plan

### 1. Native Calendar Event CRUD

```python
async def list_events(db, group_id, start_date, end_date) -> list[CalendarEvent]
async def get_event_by_id(db, event_id) -> CalendarEvent | None
async def create_event(db, group_id, created_by_id, title, event_date, ...) -> CalendarEvent
async def update_event(db, event_id, **updates) -> CalendarEvent
async def cancel_event(db, event_id) -> CalendarEvent
async def rsvp_event(db, event_id, user_id, status) -> EventAttendee
```

### 2. Reminder CRUD

```python
async def list_reminders(db, group_id, user_id=None, include_completed=False) -> list[Reminder]
async def create_reminder(db, group_id, user_id, title, due_date, priority) -> Reminder
async def complete_reminder(db, reminder_id) -> Reminder
async def delete_reminder(db, reminder_id) -> None
```

### 3. Unified Feed Aggregation

```python
@dataclass
class UnifiedCalendarItem:
    date: datetime
    title: str
    source: str  # "chore", "bill", "vaccine", "birthday", "event", etc.
    source_id: int
    source_module: str
    priority: str
    metadata: dict

async def get_unified_feed(db, group_id, start_date, end_date, sources: list[str] = None) -> list[UnifiedCalendarItem]:
    items = []

    # Native calendar events
    if "events" in sources:
        items += await _fetch_calendar_events(db, group_id, start_date, end_date)

    # Finance: recurring expenses
    if "bills" in sources:
        items += await _fetch_bill_due_dates(db, group_id, start_date, end_date)

    # Chores: assignments
    if "chores" in sources:
        items += await _fetch_chore_deadlines(db, group_id, start_date, end_date)

    # ... other sources

    return sorted(items, key=lambda x: x.date)
```

### 4. API Endpoints

| Method   | Path                                | Description               |
| -------- | ----------------------------------- | ------------------------- |
| `GET`    | `/calendar/feed`                    | Unified feed with filters |
| `GET`    | `/calendar/events`                  | List native events        |
| `POST`   | `/calendar/events`                  | Create event              |
| `GET`    | `/calendar/events/{id}`             | Get event                 |
| `PATCH`  | `/calendar/events/{id}`             | Update event              |
| `DELETE` | `/calendar/events/{id}`             | Cancel event              |
| `POST`   | `/calendar/events/{id}/rsvp`        | RSVP to event             |
| `GET`    | `/calendar/reminders`               | List reminders            |
| `POST`   | `/calendar/reminders`               | Create reminder           |
| `PATCH`  | `/calendar/reminders/{id}/complete` | Complete reminder         |

---

## Feed Response Structure

```python
class UnifiedFeedResponse(BaseModel):
    items: list[UnifiedCalendarItem]
    date_range: tuple[datetime, datetime]
    sources_included: list[str]
```

---

## Cross-Module Import Pattern

Use interface imports only:

```python
from mitlist.modules.finance.interface import list_recurring_expenses
from mitlist.modules.chores.interface import list_assignments
from mitlist.modules.pets.interface import list_medical_records
# etc.
```

---

## Files to Modify

- `[mitlist/modules/calendar/service.py](mitlist/modules/calendar/service.py)` - Add service functions
- `[mitlist/modules/calendar/interface.py](mitlist/modules/calendar/interface.py)` - Re-export functions
- `[mitlist/modules/calendar/api.py](mitlist/modules/calendar/api.py)` - Implement endpoints
- `[mitlist/modules/calendar/schemas.py](mitlist/modules/calendar/schemas.py)` - Add `UnifiedCalendarItem` schema
