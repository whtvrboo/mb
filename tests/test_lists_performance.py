import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.auth.models import Group, User
from mitlist.modules.lists.models import List


@pytest.mark.asyncio
async def test_lists_index_usage(db: AsyncSession, test_user: User, test_group: Group):
    """
    Verify that list_lists query uses the composite index ix_lists_group_archived_id.
    """
    # 1. Setup Data
    # Create some lists
    list1 = List(group_id=test_group.id, name="List 1", type="TODO", is_archived=False)
    list2 = List(group_id=test_group.id, name="List 2", type="TODO", is_archived=True)
    db.add_all([list1, list2])
    await db.commit()

    # 2. Run EXPLAIN QUERY PLAN
    # We simulate the query used in list_lists:
    # WHERE group_id = ? AND is_archived = ? ORDER BY id

    # SQLite syntax for explain
    stmt = text(
        "EXPLAIN QUERY PLAN SELECT * FROM lists "
        "WHERE group_id = :group_id AND is_archived = :is_archived ORDER BY id"
    )

    result = await db.execute(stmt, {"group_id": test_group.id, "is_archived": False})
    rows = result.fetchall()

    # 3. Verify Results
    # SQLite output format: (id, parent, notused, detail)
    # The detail column should contain "USING INDEX ix_lists_group_archived_id"

    explanation = "\n".join([str(row) for row in rows])
    print(f"Query Plan:\n{explanation}")

    # We expect usage of the composite index
    assert "USING INDEX ix_lists_group_archived_id" in explanation, (
        f"Query is not using the expected index. Plan: {explanation}"
    )

    # Also verify the case without is_archived (should still use index for group_id part)
    # With (group_id, is_archived, id), query on group_id can use the index.

    stmt_partial = text(
        "EXPLAIN QUERY PLAN SELECT * FROM lists WHERE group_id = :group_id ORDER BY id"
    )
    result_partial = await db.execute(stmt_partial, {"group_id": test_group.id})
    explanation_partial = "\n".join([str(row) for row in result_partial.fetchall()])
    print(f"Query Plan (Partial):\n{explanation_partial}")

    # It should still use the index
    assert "USING INDEX ix_lists_group_archived_id" in explanation_partial, (
        f"Query (partial) is not using the expected index. Plan: {explanation_partial}"
    )
