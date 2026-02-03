import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.auth.models import Group, User
from mitlist.modules.chores.models import Chore, ChoreAssignment, ChoreDependency
from mitlist.modules.chores.service import check_dependencies_met


# Query counter class
class QueryCounter:
    def __init__(self):
        self.count = 0

    def __call__(self, conn, cursor, statement, parameters, context, executemany):
        self.count += 1


@pytest.fixture
async def setup_data(db: AsyncSession):
    group = Group(name=f"Perf Group {uuid.uuid4()}", created_by_id=1)
    db.add(group)
    await db.flush()
    await db.refresh(group)

    user = User(
        email=f"perf_user_{uuid.uuid4()}@example.com",
        name="Perf User",
        hashed_password="pw",
        is_active=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return group, user


@pytest.mark.asyncio
async def test_check_dependencies_performance(db: AsyncSession, engine, setup_data):
    """
    Verify that check_dependencies_met runs in a constant number of queries.
    """
    group, user = setup_data

    # Create main chore
    main_chore = Chore(
        group_id=group.id,
        name="Main Chore",
        frequency_type="DAILY",
        effort_value=10,
        interval_value=1,
    )
    db.add(main_chore)
    await db.flush()

    # Create assignment for main chore
    main_assignment = ChoreAssignment(
        chore_id=main_chore.id,
        assigned_to_id=user.id,
        due_date=datetime.now(timezone.utc),
        status="PENDING",
    )
    db.add(main_assignment)
    await db.flush()

    # Create 10 dependency chores
    num_dependencies = 10
    for i in range(num_dependencies):
        dep_chore = Chore(
            group_id=group.id,
            name=f"Dep Chore {i}",
            frequency_type="DAILY",
            effort_value=5,
            interval_value=1,
        )
        db.add(dep_chore)
        await db.flush()

        # Add dependency
        dep = ChoreDependency(
            chore_id=main_chore.id,
            depends_on_chore_id=dep_chore.id,
            dependency_type="BLOCKING",
        )
        db.add(dep)

        # Add completed assignment for dependency
        assign = ChoreAssignment(
            chore_id=dep_chore.id,
            assigned_to_id=user.id,
            due_date=datetime.now(timezone.utc),
            status="COMPLETED",
            completed_at=datetime.now(timezone.utc),
        )
        db.add(assign)

    # We use flush instead of commit to allow rollback, but queries should see flushed data in same session.
    # However, for performance test, we want to ensure no pending flushes affect the query count.
    await db.commit()

    # 2. Attach Query Counter
    qc = QueryCounter()
    event.listen(engine.sync_engine, "before_cursor_execute", qc)

    # 3. Run Benchmark
    # This should return True since all dependencies are completed
    result = await check_dependencies_met(db, main_assignment.id)

    # 4. Assertions
    print(f"Queries executed: {qc.count}")

    assert result is True

    # Optimized: Should be small constant number.
    assert qc.count <= 5, f"Expected <= 5 queries, got {qc.count}. N+1 problem detected!"


@pytest.mark.asyncio
async def test_check_dependencies_correctness_mixed(db: AsyncSession, setup_data):
    """
    Verify correctness: one dependency met, one not met.
    """
    group, user = setup_data

    main_chore = Chore(
        group_id=group.id,
        name="Main Mixed",
        frequency_type="DAILY",
        effort_value=10,
        interval_value=1,
    )
    db.add(main_chore)
    await db.flush()

    assign = ChoreAssignment(
        chore_id=main_chore.id,
        assigned_to_id=user.id,
        due_date=datetime.now(timezone.utc),
        status="PENDING",
    )
    db.add(assign)
    await db.flush()

    # Dep 1: Completed
    dep1 = Chore(
        group_id=group.id, name="Dep 1", frequency_type="DAILY", effort_value=5, interval_value=1
    )
    db.add(dep1)
    await db.flush()
    db.add(
        ChoreDependency(
            chore_id=main_chore.id, depends_on_chore_id=dep1.id, dependency_type="BLOCKING"
        )
    )
    db.add(
        ChoreAssignment(
            chore_id=dep1.id,
            assigned_to_id=user.id,
            due_date=datetime.now(timezone.utc),
            status="COMPLETED",
        )
    )

    # Dep 2: Pending
    dep2 = Chore(
        group_id=group.id, name="Dep 2", frequency_type="DAILY", effort_value=5, interval_value=1
    )
    db.add(dep2)
    await db.flush()
    db.add(
        ChoreDependency(
            chore_id=main_chore.id, depends_on_chore_id=dep2.id, dependency_type="BLOCKING"
        )
    )
    db.add(
        ChoreAssignment(
            chore_id=dep2.id,
            assigned_to_id=user.id,
            due_date=datetime.now(timezone.utc),
            status="PENDING",
        )
    )

    await db.commit()

    result = await check_dependencies_met(db, assign.id)
    assert result is False


@pytest.mark.asyncio
async def test_check_dependencies_correctness_latest(db: AsyncSession, setup_data):
    """
    Verify correctness: old completed assignment, new pending assignment. Should block.
    """
    group, user = setup_data

    main_chore = Chore(
        group_id=group.id,
        name="Main Latest",
        frequency_type="DAILY",
        effort_value=10,
        interval_value=1,
    )
    db.add(main_chore)
    await db.flush()

    assign = ChoreAssignment(
        chore_id=main_chore.id,
        assigned_to_id=user.id,
        due_date=datetime.now(timezone.utc),
        status="PENDING",
    )
    db.add(assign)
    await db.flush()

    # Dep 1: Old completed, New pending
    dep1 = Chore(
        group_id=group.id, name="Dep 1", frequency_type="DAILY", effort_value=5, interval_value=1
    )
    db.add(dep1)
    await db.flush()
    db.add(
        ChoreDependency(
            chore_id=main_chore.id, depends_on_chore_id=dep1.id, dependency_type="BLOCKING"
        )
    )

    # Old completed
    db.add(
        ChoreAssignment(
            chore_id=dep1.id,
            assigned_to_id=user.id,
            due_date=datetime.now(timezone.utc) - timedelta(days=1),
            status="COMPLETED",
        )
    )
    # New pending
    db.add(
        ChoreAssignment(
            chore_id=dep1.id,
            assigned_to_id=user.id,
            due_date=datetime.now(timezone.utc),
            status="PENDING",
        )
    )

    await db.commit()

    result = await check_dependencies_met(db, assign.id)
    assert result is False
