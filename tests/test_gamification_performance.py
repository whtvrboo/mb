import pytest
import time
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession
from mitlist.modules.gamification.service import check_and_award_achievements
from mitlist.modules.gamification.models import (
    Achievement,
    AchievementCategory,
    RequirementType,
    UserPoints,
)
from mitlist.modules.chores.models import Chore, ChoreAssignment, ChoreAssignmentStatus
from mitlist.modules.auth.models import User, Group
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_gamification_n_plus_one_benchmark(
    db: AsyncSession, test_user: User, test_group: Group
):
    # Ensure user has points record so function doesn't return early
    user_points = UserPoints(
        user_id=test_user.id, group_id=test_group.id, total_points=0, monthly_points=0
    )
    db.add(user_points)

    # 1. Setup: Create 50 COUNT achievements for CHORES
    achievements = []
    for i in range(1, 51):
        achievements.append(
            Achievement(
                name=f"Chore Master {i}",
                description=f"Complete {i} chores",
                category=AchievementCategory.CHORES,
                requirement_type=RequirementType.COUNT,
                requirement_value=i,
                is_active=True,
            )
        )
    db.add_all(achievements)

    # Create a chore
    chore = Chore(group_id=test_group.id, name="Test Chore", effort_value=1, frequency_type="DAILY")
    db.add(chore)
    await db.flush()

    # Create 25 completed assignments (so the user qualifies for half the achievements)
    assignments = []
    for _ in range(25):
        assignments.append(
            ChoreAssignment(
                chore_id=chore.id,
                assigned_to_id=test_user.id,
                due_date=datetime.now(timezone.utc),
                status=ChoreAssignmentStatus.COMPLETED,
                completed_at=datetime.now(timezone.utc),
            )
        )
    db.add_all(assignments)
    # Flush to make sure data is in DB for queries
    await db.flush()

    # 2. Count queries
    query_count = 0

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal query_count
        # print(f"Query: {statement}") # Uncomment for debugging
        query_count += 1

    engine = db.bind
    sync_engine = engine.sync_engine

    event.listen(sync_engine, "before_cursor_execute", before_cursor_execute)

    try:
        start_time = time.time()
        # This function commits/flushes internally when awarding, but we are in a transaction.
        await check_and_award_achievements(db, test_user.id, test_group.id)
        end_time = time.time()
    finally:
        event.remove(sync_engine, "before_cursor_execute", before_cursor_execute)

    duration = end_time - start_time
    print(f"\n--- Benchmark Results ---")
    print(f"Time taken: {duration:.4f}s")
    print(f"Queries executed: {query_count}")

    # Expectation:
    # Baseline was ~129 queries.
    # Optimized should be around 80 queries (saved 49 queries).
    # We assert it is significantly lower than the unoptimized baseline (e.g. < 100).
    assert query_count < 100, f"Expected < 100 queries (optimized), but got {query_count}"
