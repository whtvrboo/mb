## 2024-05-23 - Polymorphic Relationship Indexing
**Learning:** The `Comment` model uses a polymorphic relationship (`parent_type`, `parent_id`) but only had an index on `parent_id`. This causes inefficient index scans when `parent_id` values collide across different types (common with autoincrement integer IDs).
**Action:** Always check polymorphic associations for composite indexes `(type, id)` or `(type, id, sort_col)`.

## 2024-05-23 - Notification Sorting Optimization
**Learning:** `list_notifications` queries by `user_id` and sorts by `created_at DESC`. The single index on `user_id` forces the database to sort results in memory after fetching.
**Action:** Add composite indexes `(filter_col, sort_col)` for frequently accessed sorted lists like feeds and activity logs.

## 2024-05-24 - Redundant Indexing with Composite Indexes
**Learning:** When adding a composite index `(col_a, col_b)` to optimize `WHERE col_a = ? ORDER BY col_b`, the existing index on `col_a` becomes redundant as the composite index can serve queries on `col_a` alone.
**Action:** Remove `index=True` from the leading column of a new composite index to save storage and write overhead.

## 2024-05-24 - Audit Log and Tag Assignment Indexing
**Learning:** `AuditLog` and `TagAssignment` tables used single-column indexing on their polymorphic identifier `entity_id`. This creates redundant indexes and inefficient database lookups when filtering by `entity_type` and `entity_id` together, which often happens with these models (e.g., fetching the history or tags for a specific entity type like an expense or chore).
**Action:** Replace single-column `entity_id` index with a composite index starting with `entity_type` (e.g., `(entity_type, entity_id)` or `(entity_type, entity_id, sort_col)`) for polymorphic relations to optimize search queries and prevent index scans.
