## 2024-05-23 - Polymorphic Relationship Indexing
**Learning:** The `Comment` model uses a polymorphic relationship (`parent_type`, `parent_id`) but only had an index on `parent_id`. This causes inefficient index scans when `parent_id` values collide across different types (common with autoincrement integer IDs).
**Action:** Always check polymorphic associations for composite indexes `(type, id)` or `(type, id, sort_col)`.

## 2024-05-23 - Notification Sorting Optimization
**Learning:** `list_notifications` queries by `user_id` and sorts by `created_at DESC`. The single index on `user_id` forces the database to sort results in memory after fetching.
**Action:** Add composite indexes `(filter_col, sort_col)` for frequently accessed sorted lists like feeds and activity logs.

## 2024-05-24 - Redundant Indexing with Composite Indexes
**Learning:** When adding a composite index `(col_a, col_b)` to optimize `WHERE col_a = ? ORDER BY col_b`, the existing index on `col_a` becomes redundant as the composite index can serve queries on `col_a` alone.
**Action:** Remove `index=True` from the leading column of a new composite index to save storage and write overhead.

## 2026-02-05 - Audit Log Polymorphic and Sorted Indexes
**Learning:** `AuditLog` queries frequently filter by polymorphic combinations `(entity_type, entity_id)` and sort by `occurred_at`. Similarly, `TagAssignment` uses polymorphic `(entity_type, entity_id)`. Previous indexes just covered `entity_id`. This causes sequential scans when there are many entities with the same ID, and manual sorts for `occurred_at`.
**Action:** Replace `entity_id` indexes with `(entity_type, entity_id, occurred_at)` for tables that filter by entity and sort by time, and `(entity_type, entity_id)` for polymorphic relationships to prevent single-column integer ID collisions.
