from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from mitlist.modules.audit.service import generate_report
from mitlist.modules.finance.models import Budget, Category, Expense


@pytest.mark.asyncio
async def test_generate_budget_report_performance(db, test_group, test_user):
    """Test generating budget status report with multiple budgets and expenses."""

    # Create Data: 5 Categories, 5 Budgets, 10 Expenses per category
    num_categories = 5
    expenses_per_category = 10
    start_date = datetime.utcnow() - timedelta(days=30)
    end_date = datetime.utcnow()

    for i in range(num_categories):
        cat = Category(group_id=test_group.id, name=f"Report Category {i}", is_income=False)
        db.add(cat)
        await db.flush()

        budget = Budget(
            group_id=test_group.id,
            category_id=cat.id,
            amount_limit=Decimal("1000.00"),
            period_type="MONTHLY",
            start_date=start_date,
        )
        db.add(budget)
        await db.flush()

        for j in range(expenses_per_category):
            expense = Expense(
                group_id=test_group.id,
                paid_by_user_id=test_user.id,
                description=f"Expense {i}-{j}",
                amount=Decimal("10.00"),
                category_id=cat.id,
                expense_date=start_date + timedelta(days=1),
            )
            db.add(expense)

    await db.flush()

    # Generate Report
    report = await generate_report(db, test_group.id, "BUDGET_STATUS", start_date, end_date)

    assert report is not None
    assert report.report_type == "BUDGET_STATUS"
    assert "budgets" in report.data_json
    assert len(report.data_json["budgets"]) == num_categories

    # Verify values for the first budget found in the report
    # Note: Report order depends on DB insertion or sorting, but we just check if any match

    budget_data = report.data_json["budgets"]
    assert len(budget_data) > 0

    for b in budget_data:
        expected_spent = expenses_per_category * 10.0
        assert b["spent"] == expected_spent
        assert b["remaining"] == 1000.0 - expected_spent
