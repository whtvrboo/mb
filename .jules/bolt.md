## 2024-05-23 - Polymorphic Relationship Indexing
**Learning:** The `Comment` model uses a polymorphic relationship (`parent_type`, `parent_id`) but only had an index on `parent_id`. This causes inefficient index scans when `parent_id` values collide across different types (common with autoincrement integer IDs).
**Action:** Always check polymorphic associations for composite indexes `(type, id)` or `(type, id, sort_col)`.

## 2024-05-23 - Notification Sorting Optimization
**Learning:** `list_notifications` queries by `user_id` and sorts by `created_at DESC`. The single index on `user_id` forces the database to sort results in memory after fetching.
**Action:** Add composite indexes `(filter_col, sort_col)` for frequently accessed sorted lists like feeds and activity logs.

## 2024-05-24 - Redundant Indexing with Composite Indexes
**Learning:** When adding a composite index `(col_a, col_b)` to optimize `WHERE col_a = ? ORDER BY col_b`, the existing index on `col_a` becomes redundant as the composite index can serve queries on `col_a` alone.
**Action:** Remove `index=True` from the leading column of a new composite index to save storage and write overhead.

## 2024-05-24 - Polymorphic Indexing
**Learning:** For polymorphic models like `AuditLog` that are frequently queried by `(entity_type, entity_id)` and sorted by `occurred_at`, adding a composite index `(entity_type, entity_id, occurred_at)` speeds up these queries by preventing expensive in-memory database sorting. The single-column index on `entity_id` also becomes redundant and should be removed.
**Action:** When creating a composite index `(col_a, col_b, col_c)`, ensure any single index on `col_a` or `col_b` that is rendered redundant is removed.
