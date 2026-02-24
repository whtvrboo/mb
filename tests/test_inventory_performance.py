
import time

import pytest
from sqlalchemy import select, text

from mitlist.modules.auth.models import Group
from mitlist.modules.lists.models import InventoryItem


@pytest.mark.asyncio
async def test_inventory_sorting_perf(db, test_user):
    """
    Benchmark inventory sorting by ID within a group.
    Verifies that the database uses an index for sorting/filtering.
    """
    # Setup - Create Group 1 (target)
    group1 = Group(name="Bench Group 1", created_by_id=test_user.id)
    db.add(group1)
    await db.flush()
    await db.refresh(group1)

    # Setup - Create Group 2 (noise)
    group2 = Group(name="Bench Group 2", created_by_id=test_user.id)
    db.add(group2)
    await db.flush()
    await db.refresh(group2)

    # Bulk insert 5,000 items into Group 1
    items1 = [
        InventoryItem(group_id=group1.id, quantity_value=i, quantity_unit="pcs")
        for i in range(5000)
    ]
    db.add_all(items1)

    # Bulk insert 5,000 items into Group 2
    items2 = [
        InventoryItem(group_id=group2.id, quantity_value=i, quantity_unit="pcs")
        for i in range(5000)
    ]
    db.add_all(items2)

    await db.commit()

    # Force analyze
    await db.execute(text("ANALYZE;"))

    # Query Group 1
    start = time.perf_counter()
    stmt = (
        select(InventoryItem)
        .where(InventoryItem.group_id == group1.id)
        .order_by(InventoryItem.id)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    end = time.perf_counter()

    print(f"\nQuery time for 5k items (with 5k noise): {(end - start) * 1000:.4f} ms")
    assert len(rows) == 5000

    # Explain
    explain_stmt = text(
        f"EXPLAIN QUERY PLAN SELECT * FROM inventory_items "
        f"WHERE group_id = {group1.id} ORDER BY id"
    )
    explain_result = await db.execute(explain_stmt)
    plan = explain_result.fetchall()

    # Check that we are using an index (not scanning table)
    # In SQLite, "USING INDEX" confirms index usage.
    # We expect "USING INDEX ix_inventory_items_group_id_id"
    plan_str = str(plan)
    print(f"\nQuery Plan: {plan_str}")

    assert "USING INDEX" in plan_str
    # Ideally check for the specific index name if possible,
    # but exact plan string varies by SQLite version
    # Just ensuring it uses SOME index is good enough for automated test
    # to prevent full scan regression
