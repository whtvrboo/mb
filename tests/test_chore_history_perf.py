from datetime import datetime, timezone

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.auth.models import Group, User
from mitlist.modules.chores.models import Chore, ChoreAssignment
from mitlist.modules.chores.service import list_chore_history


class QueryCounter:
    def __init__(self):
        self.count = 0

    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


@pytest.mark.asyncio
async def test_list_chore_history_query_count(db: AsyncSession, engine):
    """
    Verify that list_chore_history does not suffer from N+1 query problems.
    Originally, it used selectinload with join, causing 2 queries.
    Optimized, it should use contains_eager with join, causing 1 query.
    """
    # 1. Setup Data
    user = User(
        email="history_perf@example.com",
        name="History Perf User",
        hashed_password="pw",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    group = Group(name="History Perf Group", created_by_id=user.id)
    db.add(group)
    await db.flush()
    await db.refresh(group)

    chore = Chore(
        group_id=group.id,
        name="History Test Chore",
        frequency_type="DAILY",
        effort_value=1,
        interval_value=1,
    )
    db.add(chore)
    await db.flush()

    assignment = ChoreAssignment(
        chore_id=chore.id,
        assigned_to_id=user.id,
        due_date=datetime.now(timezone.utc),
        status="COMPLETED",
        completed_at=datetime.now(timezone.utc)
    )
    db.add(assignment)
    await db.commit() # Commit to ensure separate transaction for query count

    # 2. Attach Query Counter
    qc = QueryCounter()
    event.listen(engine.sync_engine, "before_cursor_execute", qc)

    # 3. Run Function
    assignments = await list_chore_history(db, group.id)

    # 4. Verify Results
    event.remove(engine.sync_engine, "before_cursor_execute", qc)

    assert len(assignments) == 1
    # Optimized: Expected 1 query (contains_eager). Before optimization: 2.
    assert qc.count == 1, f"Expected 1 query, got {qc.count}"
