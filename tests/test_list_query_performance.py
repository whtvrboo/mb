import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.auth.models import Group, User
from mitlist.modules.lists.models import List, ListType


@pytest.mark.asyncio
async def test_list_query_uses_composite_index(db: AsyncSession):
    """
    Verify that querying lists by group and archived status uses the composite index.
    """
    # Create User first to satisfy ForeignKey
    user = User(
        email="perf_test@example.com", hashed_password="pw", name="Perf User", is_active=True
    )
    db.add(user)
    await db.flush()

    # Setup data
    group = Group(name="Perf Group", created_by_id=user.id)
    db.add(group)
    await db.flush()

    # Add some lists
    for i in range(10):
        new_list = List(
            group_id=group.id,
            name=f"List {i}",
            type=ListType.TODO,
            is_archived=(i % 2 == 0),
        )
        db.add(new_list)
    await db.flush()

    # Query: list_lists with is_archived=False
    stmt = text(
        "EXPLAIN QUERY PLAN SELECT * FROM lists "
        "WHERE group_id = :group_id AND is_archived = :is_archived "
        "ORDER BY id"
    )
    result = await db.execute(stmt, {"group_id": group.id, "is_archived": False})
    plan = result.fetchall()

    plan_str = " ".join([str(row) for row in plan])

    # Check if it uses the composite index
    # We look for "ix_lists_group_archived_id" in the plan output
    assert "ix_lists_group_archived_id" in plan_str, (
        f"Query should use composite index 'ix_lists_group_archived_id', got plan: {plan_str}"
    )
