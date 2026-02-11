from datetime import datetime, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_expense_with_too_many_splits(
    client: AsyncClient, test_category, test_user, test_group
):
    """Test that creating an expense with too many splits is rejected."""

    # Create 101 splits (assuming limit should be 100)
    splits = [{"user_id": test_user.id, "owed_amount": "1.00"} for _ in range(101)]

    response = await client.post(
        "/api/v1/expenses",
        json={
            "description": "Massive Split Expense",
            "amount": "101.00",
            "currency_code": "USD",
            "category_id": test_category.id,
            "expense_date": datetime.now(timezone.utc).isoformat(),
            "payment_method": "CARD",
            "splits": splits,
        },
    )

    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_split_preset_with_too_many_members(
    client: AsyncClient, test_user, test_group
):
    """Test that creating a split preset with too many members is rejected."""

    members = [{"user_id": test_user.id, "percentage": "1.00"} for _ in range(101)]

    response = await client.post(
        "/api/v1/split-presets",
        headers={"X-Group-ID": str(test_group.id)},
        json={
            "name": "Massive Split Preset",
            "method": "PERCENTAGE",
            "is_default": False,
            "members": members,
        },
    )

    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
