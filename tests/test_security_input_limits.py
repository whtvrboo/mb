import pytest
from pydantic import ValidationError

from mitlist.modules.auth.schemas import (
    LocationBase,
    ServiceContactBase,
    InviteAcceptRequest,
    UserCreate,
    UserLoginRequest,
)
from mitlist.modules.lists.schemas import ItemBase
from mitlist.modules.documents.schemas import SharedCredentialBase, DocumentSearchRequest


def test_location_base_notes_limit():
    """Test LocationBase notes max_length."""
    with pytest.raises(ValidationError) as exc:
        LocationBase(name="Test", notes="a" * 1001)
    assert "String should have at most 1000 characters" in str(exc.value)


def test_service_contact_base_limits():
    """Test ServiceContactBase notes and address max_length."""
    # Notes
    with pytest.raises(ValidationError) as exc:
        ServiceContactBase(name="Test", job_title="PLUMBER", notes="a" * 1001)
    assert "String should have at most 1000 characters" in str(exc.value)

    # Address
    with pytest.raises(ValidationError) as exc:
        ServiceContactBase(name="Test", job_title="PLUMBER", address="a" * 501)
    assert "String should have at most 500 characters" in str(exc.value)


def test_invite_accept_request_code_limit():
    """Test InviteAcceptRequest code max_length."""
    with pytest.raises(ValidationError) as exc:
        InviteAcceptRequest(code="a" * 101)
    assert "String should have at most 100 characters" in str(exc.value)


def test_item_base_notes_limit():
    """Test ItemBase notes max_length."""
    with pytest.raises(ValidationError) as exc:
        ItemBase(name="Test", notes="a" * 1001)
    assert "String should have at most 1000 characters" in str(exc.value)


def test_shared_credential_base_notes_limit():
    """Test SharedCredentialBase notes max_length."""
    with pytest.raises(ValidationError) as exc:
        SharedCredentialBase(
            name="Test", credential_type="OTHER", access_level="MEMBER", notes="a" * 1001
        )
    assert "String should have at most 1000 characters" in str(exc.value)


def test_document_search_request_query_limit():
    """Test DocumentSearchRequest query max_length."""
    with pytest.raises(ValidationError) as exc:
        DocumentSearchRequest(group_id=1, query="a" * 256)
    assert "String should have at most 255 characters" in str(exc.value)


def test_user_password_limits():
    """Test UserCreate and UserLoginRequest password max_length."""
    # UserCreate
    with pytest.raises(ValidationError) as exc:
        UserCreate(email="test@example.com", name="Test User", password="a" * 129)
    assert "String should have at most 128 characters" in str(exc.value)

    # UserLoginRequest
    with pytest.raises(ValidationError) as exc:
        UserLoginRequest(email="test@example.com", password="a" * 129)
    assert "String should have at most 128 characters" in str(exc.value)


def test_recipe_create_ingredients_limit():
    from mitlist.modules.recipes.schemas import RecipeCreate, RecipeIngredientInput
    from pydantic import ValidationError

    try:
        RecipeCreate(
            group_id=1,
            title="test",
            prep_time_minutes=1,
            cook_time_minutes=1,
            servings=1,
            ingredients=[RecipeIngredientInput(name="i") for _ in range(101)],
        )
        assert False, "Should have failed due to max_length"
    except ValidationError as e:
        assert "List should have at most 100 items" in str(e)


def test_recipe_create_steps_limit():
    from mitlist.modules.recipes.schemas import RecipeCreate, RecipeStepInput
    from pydantic import ValidationError

    try:
        RecipeCreate(
            group_id=1,
            title="test",
            prep_time_minutes=1,
            cook_time_minutes=1,
            servings=1,
            steps=[RecipeStepInput(step_number=i, instruction="i") for i in range(1, 102)],
        )
        assert False, "Should have failed due to max_length"
    except ValidationError as e:
        assert "List should have at most 100 items" in str(e)


def test_generate_shopping_list_request_meal_plan_ids_limit():
    from mitlist.modules.recipes.schemas import GenerateShoppingListRequest
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc:
        GenerateShoppingListRequest(meal_plan_ids=[1] * 101)
    assert "List should have at most 100 items" in str(exc.value)


def test_recipe_search_request_ingredient_names_limit():
    from mitlist.modules.recipes.schemas import RecipeSearchRequest
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc:
        RecipeSearchRequest(group_id=1, ingredient_names=["i"] * 101)
    assert "List should have at most 100 items" in str(exc.value)
