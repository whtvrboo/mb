from datetime import UTC, datetime

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.auth.models import Group, User
from mitlist.modules.chores.models import Chore, ChoreAssignment
from mitlist.modules.chores.service import list_assignments


class QueryCounter:
    def __init__(self):
        self.count = 0

    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


@pytest.mark.asyncio
async def test_list_assignments_query_count(db: AsyncSession, engine):
    """
    Verify that list_assignments does not suffer from N+1 query problems.
    Originally, it used selectinload with join, causing 2 queries.
    Optimized, it should use contains_eager with join, causing 1 query.
    """
    # 1. Setup Data
    user = User(
        email="query_perf_user@example.com",
        name="Query Perf User",
        hashed_password="pw",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    group = Group(name="Query Perf Group", created_by_id=user.id)
    db.add(group)
    await db.flush()
    await db.refresh(group)

    chore = Chore(
        group_id=group.id,
        name="Query Perf Chore",
        frequency_type="DAILY",
        effort_value=5,
        interval_value=1,
    )
    db.add(chore)
    await db.flush()

    assignment = ChoreAssignment(
        chore_id=chore.id, assigned_to_id=user.id, due_date=datetime.now(UTC), status="PENDING"
    )
    db.add(assignment)
    await db.commit()

    # 2. Attach Query Counter
    qc = QueryCounter()
    event.listen(engine.sync_engine, "before_cursor_execute", qc)

    # 3. Run Function
    assignments = await list_assignments(db, group.id)

    # 4. Verify Results
    print(f"Queries executed: {qc.count}")
    assert len(assignments) == 1

    # NOTE: Before optimization, this is 2. After optimization, it should be 1.
    assert qc.count == 1, f"Expected 1 query, got {qc.count}"
