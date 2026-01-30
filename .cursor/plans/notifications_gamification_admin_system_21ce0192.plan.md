---
name: Notifications Gamification Admin System
overview: Implement notifications (in-app, comments, reactions), gamification (points, achievements, streaks, leaderboards), admin/audit (logs, reports, tags), and system/locations modules.
todos:
  - id: notifications-core
    content: Implement notifications service (list, create, mark read, unread count)
    status: completed
  - id: notifications-comments
    content: Implement comments and reactions service + endpoints
    status: completed
  - id: gamification-points
    content: Implement points tracking and awarding service + endpoints
    status: completed
  - id: gamification-achievements
    content: Implement achievements checking and awarding service + endpoints
    status: completed
  - id: gamification-streaks
    content: Implement streaks tracking service + endpoints
    status: completed
  - id: gamification-leaderboard
    content: Implement leaderboard computation service + endpoints
    status: completed
  - id: audit-logs
    content: Implement audit logging service + query endpoints
    status: completed
  - id: audit-reports
    content: Implement report generation service + endpoints
    status: completed
  - id: audit-tags
    content: Implement tagging service + endpoints
    status: completed
  - id: locations
    content: Implement locations CRUD in auth module
    status: completed
isProject: false
---

# Notifications, Gamification, Admin/Audit, System Implementation

## Notifications Module

**Models exist**: `NotificationPreference`, `Notification`, `Comment`, `Reaction`, `Mention`

**3 endpoints are stubs**

### Service Functions

```python
# Notifications
async def list_notifications(db, user_id, unread_only=False, limit=50) -> list[Notification]
async def create_notification(db, user_id, group_id, type, title, body, ...) -> Notification
async def mark_read(db, notification_id) -> Notification
async def mark_all_read(db, user_id) -> int  # Returns count marked
async def get_unread_count(db, user_id) -> int

# Preferences
async def get_preferences(db, user_id) -> list[NotificationPreference]
async def update_preference(db, user_id, event_type, channel, enabled) -> NotificationPreference

# Comments
async def list_comments(db, parent_type, parent_id) -> list[Comment]
async def create_comment(db, author_id, parent_type, parent_id, content, mentioned_user_ids) -> Comment
async def update_comment(db, comment_id, content) -> Comment
async def delete_comment(db, comment_id) -> None

# Reactions
async def toggle_reaction(db, user_id, target_type, target_id, emoji_code) -> ReactionToggleResponse
async def list_reactions(db, target_type, target_id) -> list[Reaction]
```

### API Endpoints

| Method   | Path                         | Description              |
| -------- | ---------------------------- | ------------------------ |
| `GET`    | `/notifications`             | List user notifications  |
| `PATCH`  | `/notifications/{id}/read`   | Mark as read             |
| `POST`   | `/notifications/clear`       | Mark all as read         |
| `GET`    | `/notifications/count`       | Get unread count         |
| `GET`    | `/notifications/preferences` | Get preferences          |
| `PATCH`  | `/notifications/preferences` | Update preferences       |
| `GET`    | `/comments`                  | List comments for entity |
| `POST`   | `/comments`                  | Create comment           |
| `PATCH`  | `/comments/{id}`             | Edit comment             |
| `DELETE` | `/comments/{id}`             | Delete comment           |
| `POST`   | `/reactions/toggle`          | Toggle reaction          |

---

## Gamification Module

**Models exist**: `UserPoints`, `Achievement`, `UserAchievement`, `Streak`, `Leaderboard`

**4 endpoints are stubs**

### Service Functions

```python
# Points
async def get_user_points(db, user_id, group_id) -> UserPoints
async def award_points(db, user_id, group_id, points, reason) -> UserPoints
async def reset_monthly_points(db, group_id) -> None  # Scheduled job

# Achievements
async def list_achievements(db, category=None) -> list[Achievement]
async def get_user_achievements(db, user_id) -> list[UserAchievement]
async def check_and_award_achievements(db, user_id, group_id) -> list[Achievement]
    # Check if user qualifies for any new achievements

# Streaks
async def get_user_streaks(db, user_id, group_id) -> list[Streak]
async def record_activity(db, user_id, group_id, activity_type) -> Streak
    # Updates current_streak_days, longest_streak_days

# Leaderboard
async def get_leaderboard(db, group_id, period_type, metric) -> list[LeaderboardEntry]
async def refresh_leaderboard(db, group_id) -> None  # Compute rankings
```

### API Endpoints

| Method | Path                            | Description             |
| ------ | ------------------------------- | ----------------------- |
| `GET`  | `/gamification/points`          | Get my points           |
| `POST` | `/gamification/points/award`    | Award points (admin)    |
| `GET`  | `/gamification/achievements`    | List all achievements   |
| `GET`  | `/gamification/achievements/me` | My earned achievements  |
| `GET`  | `/gamification/streaks`         | Get my streaks          |
| `POST` | `/gamification/streaks/record`  | Record activity         |
| `GET`  | `/gamification/leaderboard`     | Get group leaderboard   |
| `GET`  | `/gamification/summary`         | My gamification summary |

---

## Admin/Audit Module

**Models exist**: `AuditLog`, `ReportSnapshot`, `Tag`, `TagAssignment`

**4 endpoints are stubs**

### Service Functions

```python
# Audit Logs
async def log_action(db, group_id, user_id, action, entity_type, entity_id, old_values, new_values) -> AuditLog
async def list_audit_logs(db, group_id, entity_type=None, user_id=None, limit=100) -> list[AuditLog]
async def get_entity_history(db, entity_type, entity_id) -> list[AuditLog]

# Reports
async def generate_report(db, group_id, report_type, period_start, period_end) -> ReportSnapshot
async def list_reports(db, group_id, report_type=None) -> list[ReportSnapshot]
async def compare_reports(db, report_id_1, report_id_2) -> ReportComparisonResponse

# Tags
async def list_tags(db, group_id) -> list[Tag]
async def create_tag(db, group_id, name, color_hex) -> Tag
async def delete_tag(db, tag_id) -> None

# Tag Assignments
async def assign_tag(db, tag_id, entity_type, entity_id) -> TagAssignment
async def remove_tag_assignment(db, assignment_id) -> None
async def get_entity_tags(db, entity_type, entity_id) -> list[Tag]

# Admin
async def get_system_stats(db) -> dict
async def set_maintenance_mode(db, enabled: bool, message: str) -> None
async def broadcast_notification(db, group_id, title, body) -> int  # Returns count sent
```

### API Endpoints

| Method   | Path                      | Description            |
| -------- | ------------------------- | ---------------------- |
| `GET`    | `/admin/system-stats`     | System statistics      |
| `GET`    | `/admin/audit-trail`      | Query audit logs       |
| `POST`   | `/admin/broadcast`        | Broadcast notification |
| `POST`   | `/admin/maintenance-mode` | Toggle maintenance     |
| `GET`    | `/admin/reports`          | List generated reports |
| `POST`   | `/admin/reports/generate` | Generate new report    |
| `GET`    | `/admin/tags`             | List group tags        |
| `POST`   | `/admin/tags`             | Create tag             |
| `DELETE` | `/admin/tags/{id}`        | Delete tag             |
| `POST`   | `/admin/tags/assign`      | Assign tag to entity   |

---

## System/Locations Module

**Location model exists** in `[mitlist/modules/auth/models.py](mitlist/modules/auth/models.py)`

**2 endpoints are stubs** in `[mitlist/modules/auth/api.py](mitlist/modules/auth/api.py)`

### Service Functions (in auth/service.py)

```python
# Locations
async def list_locations(db, group_id) -> list[Location]
async def get_location_by_id(db, location_id) -> Location | None
async def create_location(db, group_id, name, floor_level, ...) -> Location
async def update_location(db, location_id, **updates) -> Location
async def delete_location(db, location_id) -> None
```

### API Endpoints

| Method   | Path              | Description          |
| -------- | ----------------- | -------------------- |
| `GET`    | `/locations`      | List group locations |
| `POST`   | `/locations`      | Create location      |
| `GET`    | `/locations/{id}` | Get location         |
| `PATCH`  | `/locations/{id}` | Update location      |
| `DELETE` | `/locations/{id}` | Delete location      |
| `GET`    | `/system/info`    | System info          |

---

## Files to Modify

**Notifications:**

- `[mitlist/modules/notifications/service.py](mitlist/modules/notifications/service.py)`
- `[mitlist/modules/notifications/api.py](mitlist/modules/notifications/api.py)`

**Gamification:**

- `[mitlist/modules/gamification/service.py](mitlist/modules/gamification/service.py)`
- `[mitlist/modules/gamification/api.py](mitlist/modules/gamification/api.py)`

**Audit:**

- `[mitlist/modules/audit/service.py](mitlist/modules/audit/service.py)`
- `[mitlist/modules/audit/api.py](mitlist/modules/audit/api.py)`

**System/Locations:**

- `[mitlist/modules/auth/service.py](mitlist/modules/auth/service.py)`
- `[mitlist/modules/auth/api.py](mitlist/modules/auth/api.py)`
- `[mitlist/api/system.py](mitlist/api/system.py)`
