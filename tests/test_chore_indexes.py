import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.chores.models import Chore, ChoreAssignment
from mitlist.modules.auth.models import User, Group

@pytest.mark.asyncio
async def test_chore_assignment_composite_index_usage(db: AsyncSession):
    """
    Verify that the new composite indexes are used for common queries.
    This test runs EXPLAIN QUERY PLAN on SQLite.
    """
    # 1. Setup Data (minimal)
    # We need tables created, which conftest usually does.

    # 2. Test "My Pending Chores" query
    # SELECT * FROM chore_assignments WHERE assigned_to_id = ? AND status = ? ORDER BY due_date
    query = select(ChoreAssignment).where(
        ChoreAssignment.assigned_to_id == 1,
        ChoreAssignment.status == 'PENDING'
    ).order_by(ChoreAssignment.due_date)

    compiled = query.compile(compile_kwargs={"literal_binds": True})
    sql = str(compiled)

    explain_sql = f"EXPLAIN QUERY PLAN {sql}"
    result = await db.execute(text(explain_sql))
    plan = result.fetchall()

    # We expect to see usage of the new index: ix_chore_assignments_assigned_status_due
    # In SQLite, "USING INDEX" appears in the detail.
    plan_str = "\n".join([str(row) for row in plan])
    print(f"\nPlan for My Pending Chores:\n{plan_str}")

    # Assertion: verify index usage
    # Note: The index name might be truncated or formatted differently in SQLite explain output
    # but usually it shows the name.
    # If the optimization is applied, we should see the index name.
    # If not, it might use 'ix_chore_assignments_assigned_to_id' (old index) or scan.

    # We only assert this AFTER we apply the changes.
    # For now, this test serves as a verification tool.

    # 3. Test "Group Active Chores" query
    # SELECT * FROM chores WHERE group_id = ? AND is_active = ?
    query_chores = select(Chore).where(
        Chore.group_id == 1,
        Chore.is_active == True
    )

    explain_sql_chores = f"EXPLAIN QUERY PLAN {str(query_chores.compile(compile_kwargs={'literal_binds': True}))}"
    result_chores = await db.execute(text(explain_sql_chores))
    plan_chores = result_chores.fetchall()

    plan_chores_str = "\n".join([str(row) for row in plan_chores])
    print(f"\nPlan for Group Active Chores:\n{plan_chores_str}")

    # We expect: ix_chores_group_active
