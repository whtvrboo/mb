import random
from datetime import UTC, datetime

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.auth.models import Group, User
from mitlist.modules.chores.models import Chore, ChoreAssignment
from mitlist.modules.chores.service import get_leaderboard


# Query counter class
class QueryCounter:
    def __init__(self):
        self.count = 0

    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


@pytest.mark.asyncio
async def test_leaderboard_performance(db: AsyncSession, engine):
    """
    Verify that get_leaderboard runs in a constant number of queries (optimized),
    regardless of the number of users.
    """
    # 1. Setup Data
    # Create Group
    group = Group(name="Perf Group", created_by_id=1)
    db.add(group)
    await db.flush()
    await db.refresh(group)

    # Create 10 Users
    users = []
    for i in range(10):
        user = User(
            email=f"perf_user{i}@example.com",
            name=f"Perf User {i}",
            hashed_password="pw",
            is_active=True,
        )
        db.add(user)
        users.append(user)
    await db.flush()

    # Create 5 Chores
    chores = []
    for i in range(5):
        chore = Chore(
            group_id=group.id,
            name=f"Chore {i}",
            frequency_type="DAILY",
            effort_value=10,
            interval_value=1,
        )
        db.add(chore)
        chores.append(chore)
    await db.flush()

    # Create Assignments (50 per user)
    for user in users:
        for _ in range(50):
            chore = random.choice(chores)
            status = random.choice(["COMPLETED", "PENDING", "SKIPPED"])
            assignment = ChoreAssignment(
                chore_id=chore.id,
                assigned_to_id=user.id,
                due_date=datetime.now(UTC),
                status=status,
                completed_at=datetime.now(UTC) if status == "COMPLETED" else None,
                quality_rating=random.randint(1, 5) if status == "COMPLETED" else None,
            )
            db.add(assignment)
    await db.commit()

    # 2. Attach Query Counter
    qc = QueryCounter()
    event.listen(engine.sync_engine, "before_cursor_execute", qc)

    # 3. Run Benchmark
    leaderboard = await get_leaderboard(db, group.id)

    # 4. Assertions
    # With N+1 issue, this would be 1 (users) + 10 (users) * 2 (stats) = 21 queries.
    # Optimized: Should be 1 query.
    # Allowing slight margin if implementation details change (e.g. transaction management), but definitely < 5.
    print(f"Queries executed: {qc.count}")
    assert qc.count <= 2, f"Expected <= 2 queries, got {qc.count}. N+1 problem detected!"

    assert len(leaderboard) == 10

    # Verify data integrity for first user
    first_entry = leaderboard[0]
    assert "total_effort_points" in first_entry
    assert "completion_rate" in first_entry
    assert first_entry["total_assigned"] == 50
    assert first_entry["total_effort_points"] == first_entry["completed"] * 10
