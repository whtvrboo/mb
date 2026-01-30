"""Tests for finance module."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.finance.models import (
    Budget,
    Category,
    Expense,
    ExpenseSplit,
    RecurringExpense,
    Settlement,
    SplitPreset,
)


class TestCategories:
    """Test category endpoints."""

    async def test_create_category(self, client: AsyncClient, test_group):
        """Test creating a category."""
        response = await client.post(
            "/api/v1/categories",
            json={
                "group_id": test_group.id,
                "name": "Utilities",
                "icon_emoji": "⚡",
                "color_hex": "#3498db",
                "is_income": False,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Utilities"
        assert data["icon_emoji"] == "⚡"
        assert data["color_hex"] == "#3498db"

    async def test_list_categories(self, client: AsyncClient, test_category):
        """Test listing categories."""
        response = await client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(c["id"] == test_category.id for c in data)

    async def test_get_category(self, client: AsyncClient, test_category):
        """Test getting a category."""
        response = await client.get(f"/api/v1/categories/{test_category.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == test_category.name

    async def test_update_category(self, client: AsyncClient, test_category):
        """Test updating a category."""
        response = await client.patch(
            f"/api/v1/categories/{test_category.id}",
            json={"name": "Food & Groceries"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Food & Groceries"

    async def test_delete_category(self, client: AsyncClient, db: AsyncSession, test_group):
        """Test deleting a category."""
        category = Category(
            group_id=test_group.id,
            name="Delete Me",
            is_income=False,
        )
        db.add(category)
        await db.flush()
        await db.refresh(category)

        response = await client.delete(f"/api/v1/categories/{category.id}")
        assert response.status_code == 204


class TestExpenses:
    """Test expense endpoints."""

    async def test_create_expense(self, client: AsyncClient, test_category, test_user):
        """Test creating an expense."""
        response = await client.post(
            "/api/v1/expenses",
            json={
                "description": "Weekly groceries",
                "amount": "125.50",
                "currency_code": "USD",
                "category_id": test_category.id,
                "expense_date": datetime.now(timezone.utc).isoformat(),
                "payment_method": "CARD",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Weekly groceries"
        assert Decimal(data["amount"]) == Decimal("125.50")
        assert data["paid_by_user_id"] == test_user.id

    async def test_list_expenses(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test listing expenses."""
        expense = Expense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Test expense",
            amount=Decimal("50.00"),
            category_id=test_category.id,
            expense_date=datetime.now(timezone.utc),
            currency_code="USD",
        )
        db.add(expense)
        await db.flush()

        response = await client.get("/api/v1/expenses")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(e["description"] == "Test expense" for e in data)

    async def test_get_expense(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test getting an expense."""
        expense = Expense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Get me",
            amount=Decimal("75.00"),
            category_id=test_category.id,
            expense_date=datetime.now(timezone.utc),
            currency_code="USD",
        )
        db.add(expense)
        await db.flush()
        await db.refresh(expense)

        response = await client.get(f"/api/v1/expenses/{expense.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == expense.id
        assert data["description"] == "Get me"

    async def test_update_expense(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test updating an expense."""
        expense = Expense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Update me",
            amount=Decimal("100.00"),
            category_id=test_category.id,
            expense_date=datetime.now(timezone.utc),
            currency_code="USD",
            version_id=1,
        )
        db.add(expense)
        await db.flush()
        await db.refresh(expense)

        response = await client.patch(
            f"/api/v1/expenses/{expense.id}",
            json={
                "description": "Updated expense",
                "amount": "150.00",
                "version_id": 1,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated expense"
        assert Decimal(data["amount"]) == Decimal("150.00")

    async def test_delete_expense(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test deleting an expense."""
        expense = Expense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Delete me",
            amount=Decimal("25.00"),
            category_id=test_category.id,
            expense_date=datetime.now(timezone.utc),
            currency_code="USD",
        )
        db.add(expense)
        await db.flush()
        await db.refresh(expense)

        response = await client.delete(f"/api/v1/expenses/{expense.id}")
        assert response.status_code == 204


class TestBalances:
    """Test balance endpoints."""

    async def test_get_balances(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_user2, test_group):
        """Test calculating group balances."""
        from mitlist.modules.auth.models import UserGroup

        membership2 = UserGroup(
            user_id=test_user2.id,
            group_id=test_group.id,
            role="MEMBER",
            joined_at=datetime.now(timezone.utc),
        )
        db.add(membership2)
        await db.flush()

        expense = Expense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Shared expense",
            amount=Decimal("100.00"),
            category_id=test_category.id,
            expense_date=datetime.now(timezone.utc),
            currency_code="USD",
        )
        db.add(expense)
        await db.flush()
        await db.refresh(expense)

        split = ExpenseSplit(
            expense_id=expense.id,
            user_id=test_user2.id,
            owed_amount=Decimal("50.00"),
            is_paid=False,
        )
        db.add(split)
        await db.flush()

        response = await client.get("/api/v1/balances")
        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == test_group.id
        assert len(data["balances"]) >= 2

    async def test_get_balance_history(self, client: AsyncClient, test_group):
        """Test getting balance history."""
        response = await client.get(
            "/api/v1/balances/history",
            headers={"X-Group-ID": str(test_group.id)},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSettlements:
    """Test settlement endpoints."""

    async def test_create_settlement(self, client: AsyncClient, test_user, test_user2, test_group, db: AsyncSession):
        """Test creating a settlement."""
        from mitlist.modules.auth.models import UserGroup

        membership2 = UserGroup(
            user_id=test_user2.id,
            group_id=test_group.id,
            role="MEMBER",
            joined_at=datetime.now(timezone.utc),
        )
        db.add(membership2)
        await db.flush()

        response = await client.post(
            "/api/v1/settlements",
            json={
                "payee_id": test_user2.id,
                "amount": "50.00",
                "currency_code": "USD",
                "method": "VENMO",
                "settled_at": datetime.now(timezone.utc).isoformat(),
                "notes": "Splitting groceries",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert Decimal(data["amount"]) == Decimal("50.00")
        assert data["payer_id"] == test_user.id
        assert data["payee_id"] == test_user2.id

    async def test_list_settlements(self, client: AsyncClient, db: AsyncSession, test_user, test_user2, test_group):
        """Test listing settlements."""
        settlement = Settlement(
            group_id=test_group.id,
            payer_id=test_user.id,
            payee_id=test_user2.id,
            amount=Decimal("75.00"),
            currency_code="USD",
            method="CASH",
            settled_at=datetime.now(timezone.utc),
        )
        db.add(settlement)
        await db.flush()

        response = await client.get("/api/v1/settlements")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_settlement(self, client: AsyncClient, db: AsyncSession, test_user, test_user2, test_group):
        """Test getting a settlement."""
        settlement = Settlement(
            group_id=test_group.id,
            payer_id=test_user.id,
            payee_id=test_user2.id,
            amount=Decimal("100.00"),
            currency_code="USD",
            method="ZELLE",
            settled_at=datetime.now(timezone.utc),
        )
        db.add(settlement)
        await db.flush()
        await db.refresh(settlement)

        response = await client.get(f"/api/v1/settlements/{settlement.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == settlement.id

    async def test_delete_settlement(self, client: AsyncClient, db: AsyncSession, test_user, test_user2, test_group):
        """Test deleting a settlement."""
        settlement = Settlement(
            group_id=test_group.id,
            payer_id=test_user.id,
            payee_id=test_user2.id,
            amount=Decimal("25.00"),
            currency_code="USD",
            method="CASH",
            settled_at=datetime.now(timezone.utc),
        )
        db.add(settlement)
        await db.flush()
        await db.refresh(settlement)

        response = await client.delete(f"/api/v1/settlements/{settlement.id}")
        assert response.status_code == 204


class TestBudgets:
    """Test budget endpoints."""

    async def test_create_budget(self, client: AsyncClient, test_category):
        """Test creating a budget."""
        response = await client.post(
            "/api/v1/budgets",
            json={
                "category_id": test_category.id,
                "amount_limit": "500.00",
                "currency_code": "USD",
                "period_type": "MONTHLY",
                "start_date": datetime.now(timezone.utc).isoformat(),
                "alert_threshold_percentage": 80,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert Decimal(data["amount_limit"]) == Decimal("500.00")
        assert data["period_type"] == "MONTHLY"

    async def test_list_budgets(self, client: AsyncClient, db: AsyncSession, test_category, test_group):
        """Test listing budgets."""
        budget = Budget(
            group_id=test_group.id,
            category_id=test_category.id,
            amount_limit=Decimal("300.00"),
            currency_code="USD",
            period_type="WEEKLY",
            start_date=datetime.now(timezone.utc),
            alert_threshold_percentage=75,
        )
        db.add(budget)
        await db.flush()

        response = await client.get("/api/v1/budgets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_budget(self, client: AsyncClient, db: AsyncSession, test_category, test_group):
        """Test getting a budget with status."""
        budget = Budget(
            group_id=test_group.id,
            category_id=test_category.id,
            amount_limit=Decimal("200.00"),
            currency_code="USD",
            period_type="MONTHLY",
            start_date=datetime.now(timezone.utc),
            alert_threshold_percentage=80,
        )
        db.add(budget)
        await db.flush()
        await db.refresh(budget)

        response = await client.get(f"/api/v1/budgets/{budget.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == budget.id
        assert "current_spent" in data
        assert "percentage_used" in data

    async def test_update_budget(self, client: AsyncClient, db: AsyncSession, test_category, test_group):
        """Test updating a budget."""
        budget = Budget(
            group_id=test_group.id,
            category_id=test_category.id,
            amount_limit=Decimal("400.00"),
            currency_code="USD",
            period_type="MONTHLY",
            start_date=datetime.now(timezone.utc),
            alert_threshold_percentage=80,
        )
        db.add(budget)
        await db.flush()
        await db.refresh(budget)

        response = await client.patch(
            f"/api/v1/budgets/{budget.id}",
            json={"amount_limit": "600.00"},
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["amount_limit"]) == Decimal("600.00")

    async def test_delete_budget(self, client: AsyncClient, db: AsyncSession, test_category, test_group):
        """Test deleting a budget."""
        budget = Budget(
            group_id=test_group.id,
            category_id=test_category.id,
            amount_limit=Decimal("100.00"),
            currency_code="USD",
            period_type="WEEKLY",
            start_date=datetime.now(timezone.utc),
            alert_threshold_percentage=80,
        )
        db.add(budget)
        await db.flush()
        await db.refresh(budget)

        response = await client.delete(f"/api/v1/budgets/{budget.id}")
        assert response.status_code == 204


class TestRecurringExpenses:
    """Test recurring expense endpoints."""

    async def test_create_recurring_expense(self, client: AsyncClient, test_category):
        """Test creating a recurring expense."""
        response = await client.post(
            "/api/v1/recurring-expenses",
            json={
                "description": "Monthly rent",
                "amount": "1200.00",
                "currency_code": "USD",
                "category_id": test_category.id,
                "frequency_type": "MONTHLY",
                "interval_value": 1,
                "start_date": datetime.now(timezone.utc).isoformat(),
                "auto_create_expense": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Monthly rent"
        assert Decimal(data["amount"]) == Decimal("1200.00")
        assert data["frequency_type"] == "MONTHLY"

    async def test_list_recurring_expenses(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test listing recurring expenses."""
        recurring = RecurringExpense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Weekly groceries",
            amount=Decimal("100.00"),
            currency_code="USD",
            category_id=test_category.id,
            frequency_type="WEEKLY",
            interval_value=1,
            start_date=datetime.now(timezone.utc),
            next_due_date=datetime.now(timezone.utc) + timedelta(days=7),
            auto_create_expense=True,
            is_active=True,
        )
        db.add(recurring)
        await db.flush()

        response = await client.get("/api/v1/recurring-expenses")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_recurring_expense(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test getting a recurring expense."""
        recurring = RecurringExpense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Quarterly insurance",
            amount=Decimal("300.00"),
            currency_code="USD",
            category_id=test_category.id,
            frequency_type="MONTHLY",
            interval_value=3,
            start_date=datetime.now(timezone.utc),
            next_due_date=datetime.now(timezone.utc) + timedelta(days=90),
            auto_create_expense=False,
            is_active=True,
        )
        db.add(recurring)
        await db.flush()
        await db.refresh(recurring)

        response = await client.get(f"/api/v1/recurring-expenses/{recurring.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recurring.id

    async def test_update_recurring_expense(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test updating a recurring expense."""
        recurring = RecurringExpense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Update me",
            amount=Decimal("50.00"),
            currency_code="USD",
            category_id=test_category.id,
            frequency_type="WEEKLY",
            interval_value=1,
            start_date=datetime.now(timezone.utc),
            next_due_date=datetime.now(timezone.utc) + timedelta(days=7),
            auto_create_expense=True,
            is_active=True,
        )
        db.add(recurring)
        await db.flush()
        await db.refresh(recurring)

        response = await client.patch(
            f"/api/v1/recurring-expenses/{recurring.id}",
            json={"amount": "75.00"},
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(data["amount"]) == Decimal("75.00")

    async def test_delete_recurring_expense(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test deactivating a recurring expense."""
        recurring = RecurringExpense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Delete me",
            amount=Decimal("25.00"),
            currency_code="USD",
            category_id=test_category.id,
            frequency_type="MONTHLY",
            interval_value=1,
            start_date=datetime.now(timezone.utc),
            next_due_date=datetime.now(timezone.utc) + timedelta(days=30),
            auto_create_expense=True,
            is_active=True,
        )
        db.add(recurring)
        await db.flush()
        await db.refresh(recurring)

        response = await client.delete(f"/api/v1/recurring-expenses/{recurring.id}")
        assert response.status_code == 204

    async def test_generate_expense_from_recurring(self, client: AsyncClient, db: AsyncSession, test_category, test_user, test_group):
        """Test generating an expense from recurring template."""
        recurring = RecurringExpense(
            group_id=test_group.id,
            paid_by_user_id=test_user.id,
            description="Generate expense",
            amount=Decimal("200.00"),
            currency_code="USD",
            category_id=test_category.id,
            frequency_type="MONTHLY",
            interval_value=1,
            start_date=datetime.now(timezone.utc),
            next_due_date=datetime.now(timezone.utc) + timedelta(days=30),
            auto_create_expense=True,
            is_active=True,
        )
        db.add(recurring)
        await db.flush()
        await db.refresh(recurring)

        response = await client.post(f"/api/v1/recurring-expenses/{recurring.id}/generate")
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Generate expense"
        assert Decimal(data["amount"]) == Decimal("200.00")
        assert data["is_recurring_generated"] is True


class TestSplitPresets:
    """Test split preset endpoints."""

    async def test_create_split_preset(self, client: AsyncClient, test_user, test_user2, test_group):
        """Test creating a split preset."""
        response = await client.post(
            "/api/v1/split-presets",
            headers={"X-Group-ID": str(test_group.id)},
            json={
                "name": "Equal Split",
                "method": "EQUAL",
                "is_default": True,
                "members": [
                    {"user_id": test_user.id, "percentage": "50.00"},
                    {"user_id": test_user2.id, "percentage": "50.00"},
                ],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Equal Split"
        assert data["method"] == "EQUAL"
        assert len(data["members"]) == 2

    async def test_list_split_presets(self, client: AsyncClient, db: AsyncSession, test_user, test_group):
        """Test listing split presets."""
        preset = SplitPreset(
            group_id=test_group.id,
            name="Custom Split",
            method="PERCENTAGE",
            is_default=False,
        )
        db.add(preset)
        await db.flush()

        response = await client.get("/api/v1/split-presets")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1

    async def test_get_split_preset(self, client: AsyncClient, db: AsyncSession, test_group):
        """Test getting a split preset."""
        preset = SplitPreset(
            group_id=test_group.id,
            name="Get Me",
            method="FIXED_AMOUNT",
            is_default=False,
        )
        db.add(preset)
        await db.flush()
        await db.refresh(preset)

        response = await client.get(f"/api/v1/split-presets/{preset.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == preset.id
        assert data["name"] == "Get Me"

    async def test_update_split_preset(self, client: AsyncClient, db: AsyncSession, test_group):
        """Test updating a split preset."""
        preset = SplitPreset(
            group_id=test_group.id,
            name="Update Me",
            method="EQUAL",
            is_default=False,
        )
        db.add(preset)
        await db.flush()
        await db.refresh(preset)

        response = await client.patch(
            f"/api/v1/split-presets/{preset.id}",
            json={"name": "Updated Preset"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Preset"

    async def test_delete_split_preset(self, client: AsyncClient, db: AsyncSession, test_group):
        """Test deleting a split preset."""
        preset = SplitPreset(
            group_id=test_group.id,
            name="Delete Me",
            method="EQUAL",
            is_default=False,
        )
        db.add(preset)
        await db.flush()
        await db.refresh(preset)

        response = await client.delete(f"/api/v1/split-presets/{preset.id}")
        assert response.status_code == 204
