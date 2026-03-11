## 2024-05-23 - Polymorphic Relationship Indexing
**Learning:** The `Comment` model uses a polymorphic relationship (`parent_type`, `parent_id`) but only had an index on `parent_id`. This causes inefficient index scans when `parent_id` values collide across different types (common with autoincrement integer IDs).
**Action:** Always check polymorphic associations for composite indexes `(type, id)` or `(type, id, sort_col)`.

## 2024-05-23 - Notification Sorting Optimization
**Learning:** `list_notifications` queries by `user_id` and sorts by `created_at DESC`. The single index on `user_id` forces the database to sort results in memory after fetching.
**Action:** Add composite indexes `(filter_col, sort_col)` for frequently accessed sorted lists like feeds and activity logs.

## 2024-05-24 - Redundant Indexing with Composite Indexes
**Learning:** When adding a composite index `(col_a, col_b)` to optimize `WHERE col_a = ? ORDER BY col_b`, the existing index on `col_a` becomes redundant as the composite index can serve queries on `col_a` alone.
**Action:** Remove `index=True` from the leading column of a new composite index to save storage and write overhead.

## 2026-03-01 - Audit Logs Composite Index
**Learning:** The `get_entity_history` query in `mitlist/modules/audit/service.py` filters by `entity_type` and `entity_id` and then sorts by `occurred_at`. The previous model had only a single-column index on `entity_id`. This meant the database still had to scan rows for the correct `entity_type` and then perform an in-memory sort by `occurred_at`.
**Action:** When filtering by multiple exact matches and sorting by a timestamp, replace single-column indexes with a composite index (e.g., `(entity_type, entity_id, occurred_at)`). This allows the database to locate the exact subset of rows and return them pre-sorted, entirely eliminating the in-memory sort step. Also, remember to remove the `index=True` attribute from the individual column definitions in SQLAlchemy when creating a composite index via `__table_args__` to avoid redundant indexing.
