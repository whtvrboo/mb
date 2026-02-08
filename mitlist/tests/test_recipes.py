from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_recipes_list_empty(authed_client: AsyncClient, auth_headers: dict):
    """List recipes when none exist."""
    response = await authed_client.get("/recipes", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_recipes_create_and_get(authed_client: AsyncClient, auth_headers: dict):
    """Create a recipe and get it by ID."""
    recipe_data = {
        "group_id": int(auth_headers["X-Group-ID"]),
        "title": "Test Pasta",
        "description": "Simple pasta dish",
        "cuisine_type": "Italian",
        "difficulty": "EASY",
        "prep_time_minutes": 10,
        "cook_time_minutes": 15,
        "servings": 4,
        "ingredients": [
            {"name": "Pasta", "quantity_value": 400, "quantity_unit": "g", "is_optional": False},
            {
                "name": "Tomato sauce",
                "quantity_value": 1,
                "quantity_unit": "cup",
                "is_optional": False,
            },
        ],
        "steps": [
            {"step_number": 1, "instruction": "Boil water and cook pasta."},
            {"step_number": 2, "instruction": "Heat sauce and combine."},
        ],
    }
    response = await authed_client.post("/recipes", json=recipe_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    recipe_id = data["id"]
    assert data["title"] == "Test Pasta"
    assert data["servings"] == 4
    assert len(data["ingredients"]) == 2
    assert len(data["steps"]) == 2

    response = await authed_client.get(f"/recipes/{recipe_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Pasta"


@pytest.mark.asyncio
async def test_recipes_list_with_filters(authed_client: AsyncClient, auth_headers: dict):
    """List recipes and filter by cuisine/difficulty."""
    response = await authed_client.get("/recipes", headers=auth_headers)
    assert response.status_code == 200

    response = await authed_client.get("/recipes?cuisine_type=Italian", headers=auth_headers)
    assert response.status_code == 200

    response = await authed_client.get("/recipes?difficulty=EASY", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_meal_plans_create_and_list(authed_client: AsyncClient, auth_headers: dict):
    """Create a meal plan and get weekly meal plans."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    plan_date = week_start

    plan_data = {
        "group_id": int(auth_headers["X-Group-ID"]),
        "plan_date": plan_date.isoformat(),
        "meal_type": "DINNER",
        "notes": "Test meal",
    }
    response = await authed_client.post("/meal-plans", json=plan_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["meal_type"] == "DINNER"
    assert data["plan_date"] == plan_date.isoformat()

    response = await authed_client.get("/meal-plans", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "meal_plans" in data
    assert "week_start" in data
    assert "total_meals_planned" in data
    assert data["total_meals_planned"] >= 1


@pytest.mark.asyncio
async def test_recipes_sync_to_list(authed_client: AsyncClient, auth_headers: dict):
    """Create recipe, create list, sync recipe ingredients to list."""
    recipe_data = {
        "group_id": int(auth_headers["X-Group-ID"]),
        "title": "Sync Test Recipe",
        "prep_time_minutes": 5,
        "cook_time_minutes": 10,
        "servings": 2,
        "ingredients": [
            {"name": "Flour", "quantity_value": 200, "quantity_unit": "g"},
            {"name": "Sugar", "quantity_value": 50, "quantity_unit": "g"},
        ],
        "steps": [{"step_number": 1, "instruction": "Mix."}],
    }
    response = await authed_client.post("/recipes", json=recipe_data, headers=auth_headers)
    assert response.status_code == 201
    recipe_id = response.json()["id"]

    list_data = {
        "group_id": int(auth_headers["X-Group-ID"]),
        "name": "Test Shopping List",
        "type": "SHOPPING",
    }
    response = await authed_client.post("/lists", json=list_data, headers=auth_headers)
    assert response.status_code == 201
    list_id = response.json()["id"]

    response = await authed_client.post(
        f"/recipes/{recipe_id}/sync-to-list?list_id={list_id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items_added" in data
    assert "items" in data
    assert data["items_added"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_meal_plans_eager_loading(authed_client: AsyncClient, auth_headers: dict):
    """Verify that meal plans endpoint returns recipes with ingredients and steps correctly."""
    # 1. Create a recipe with ingredients and steps
    recipe_data = {
        "group_id": int(auth_headers["X-Group-ID"]),
        "title": "Complex Recipe",
        "prep_time_minutes": 10,
        "cook_time_minutes": 20,
        "servings": 2,
        "ingredients": [
            {"name": "Ingredient 1", "quantity_value": 100, "quantity_unit": "g"},
            {"name": "Ingredient 2", "quantity_value": 2, "quantity_unit": "pcs"},
        ],
        "steps": [
            {"step_number": 1, "instruction": "Step 1"},
            {"step_number": 2, "instruction": "Step 2"},
        ],
    }
    resp = await authed_client.post("/recipes", json=recipe_data, headers=auth_headers)
    assert resp.status_code == 201
    recipe_id = resp.json()["id"]

    # 2. Create a meal plan using this recipe
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    plan_date = week_start

    plan_data = {
        "group_id": int(auth_headers["X-Group-ID"]),
        "plan_date": plan_date.isoformat(),
        "meal_type": "LUNCH",
        "recipe_id": recipe_id,
    }
    resp = await authed_client.post("/meal-plans", json=plan_data, headers=auth_headers)
    assert resp.status_code == 201

    # 3. List meal plans and verify recipe details are present
    resp = await authed_client.get(
        f"/meal-plans?week_start={week_start.isoformat()}", headers=auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()

    assert data["total_meals_planned"] >= 1
    found = False
    for mp in data["meal_plans"]:
        if mp["recipe"] and mp["recipe"]["id"] == recipe_id:
            found = True
            recipe = mp["recipe"]
            assert recipe["title"] == "Complex Recipe"
            assert len(recipe["ingredients"]) == 2
            assert len(recipe["steps"]) == 2
            assert recipe["ingredients"][0]["name"] == "Ingredient 1"
            break
    assert found, "Created meal plan with recipe not found or recipe details missing"
