from datetime import UTC

import pytest
from pydantic import ValidationError

from mitlist.modules.auth.schemas import (
    InviteAcceptRequest,
    LocationBase,
    ServiceContactBase,
    UserCreate,
    UserLoginRequest,
)
from mitlist.modules.documents.schemas import DocumentSearchRequest, SharedCredentialBase
from mitlist.modules.lists.schemas import ItemBase


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


def test_calendar_event_attendee_limit():
    """Test CalendarEventCreate attendee limit."""
    from datetime import datetime

    from mitlist.modules.calendar.schemas import CalendarEventCreate

    with pytest.raises(ValidationError) as exc:
        CalendarEventCreate(
            title="Test Event",
            event_date=datetime.now(UTC),
            category="OTHER",
            group_id=1,
            attendee_ids=[i for i in range(101)],
        )
    assert "List should have at most 100 items" in str(exc.value)


def test_governance_proposal_ballot_options_limit():
    """Test ProposalCreate ballot options limit."""
    from mitlist.modules.governance.schemas import BallotOptionInput, ProposalCreate

    with pytest.raises(ValidationError) as exc:
        ProposalCreate(
            title="Test Proposal",
            description="Test Description",
            group_id=1,
            ballot_options=[BallotOptionInput(text=f"Option {i}") for i in range(101)],
        )
    assert "List should have at most 100 items" in str(exc.value)


def test_notifications_mentioned_users_limit():
    """Test CommentCreate mentioned users limit."""
    from mitlist.modules.notifications.schemas import CommentCreate

    with pytest.raises(ValidationError) as exc:
        CommentCreate(
            content="Test content",
            mentioned_user_ids=[i for i in range(101)],
        )
    assert "List should have at most 100 items" in str(exc.value)


def test_recipes_ingredients_limit():
    """Test RecipeCreate ingredients limit."""
    from mitlist.modules.recipes.schemas import RecipeCreate, RecipeIngredientInput

    with pytest.raises(ValidationError) as exc:
        RecipeCreate(
            title="Test Recipe",
            prep_time_minutes=10,
            cook_time_minutes=10,
            servings=4,
            group_id=1,
            ingredients=[RecipeIngredientInput(name=f"Ingredient {i}") for i in range(101)],
        )
    assert "List should have at most 100 items" in str(exc.value)


def test_recipes_steps_limit():
    """Test RecipeCreate steps limit."""
    from mitlist.modules.recipes.schemas import RecipeCreate, RecipeStepInput

    with pytest.raises(ValidationError) as exc:
        RecipeCreate(
            title="Test Recipe",
            prep_time_minutes=10,
            cook_time_minutes=10,
            servings=4,
            group_id=1,
            steps=[RecipeStepInput(step_number=i, instruction=f"Step {i}") for i in range(1, 102)],
        )
    assert "List should have at most 100 items" in str(exc.value)
