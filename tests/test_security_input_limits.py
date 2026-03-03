import pytest
from pydantic import ValidationError

from mitlist.modules.auth.schemas import (
    InviteAcceptRequest,
    LocationBase,
    ServiceContactBase,
    UserCreate,
    UserLoginRequest,
)
from mitlist.modules.calendar.schemas import CalendarEventCreate
from mitlist.modules.documents.schemas import DocumentSearchRequest, SharedCredentialBase
from mitlist.modules.governance.schemas import ProposalCreate
from mitlist.modules.lists.schemas import ItemBase
from mitlist.modules.notifications.schemas import CommentCreate
from mitlist.modules.recipes.schemas import RecipeCreate


def test_location_base_notes_limit():
    """Test LocationBase notes max_length."""
    with pytest.raises(ValidationError) as exc:
        LocationBase(
            name="Test",
            notes="a" * 1001
        )
    assert "String should have at most 1000 characters" in str(exc.value)

def test_service_contact_base_limits():
    """Test ServiceContactBase notes and address max_length."""
    # Notes
    with pytest.raises(ValidationError) as exc:
        ServiceContactBase(
            name="Test",
            job_title="PLUMBER",
            notes="a" * 1001
        )
    assert "String should have at most 1000 characters" in str(exc.value)

    # Address
    with pytest.raises(ValidationError) as exc:
        ServiceContactBase(
            name="Test",
            job_title="PLUMBER",
            address="a" * 501
        )
    assert "String should have at most 500 characters" in str(exc.value)

def test_invite_accept_request_code_limit():
    """Test InviteAcceptRequest code max_length."""
    with pytest.raises(ValidationError) as exc:
        InviteAcceptRequest(code="a" * 101)
    assert "String should have at most 100 characters" in str(exc.value)

def test_item_base_notes_limit():
    """Test ItemBase notes max_length."""
    with pytest.raises(ValidationError) as exc:
        ItemBase(
            name="Test",
            notes="a" * 1001
        )
    assert "String should have at most 1000 characters" in str(exc.value)

def test_shared_credential_base_notes_limit():
    """Test SharedCredentialBase notes max_length."""
    with pytest.raises(ValidationError) as exc:
        SharedCredentialBase(
            name="Test",
            credential_type="OTHER",
            access_level="MEMBER",
            notes="a" * 1001
        )
    assert "String should have at most 1000 characters" in str(exc.value)

def test_document_search_request_query_limit():
    """Test DocumentSearchRequest query max_length."""
    with pytest.raises(ValidationError) as exc:
        DocumentSearchRequest(
            group_id=1,
            query="a" * 256
        )
    assert "String should have at most 255 characters" in str(exc.value)


def test_user_password_limits():
    """Test UserCreate and UserLoginRequest password max_length."""
    # UserCreate
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            email="test@example.com",
            name="Test User",
            password="a" * 129
        )
    assert "String should have at most 128 characters" in str(exc.value)

    # UserLoginRequest
    with pytest.raises(ValidationError) as exc:
        UserLoginRequest(
            email="test@example.com",
            password="a" * 129
        )
    assert "String should have at most 128 characters" in str(exc.value)


def test_recipe_create_limits():
    """Test RecipeCreate list input limits."""
    with pytest.raises(ValidationError) as exc:
        RecipeCreate(
            title="Test",
            prep_time_minutes=10,
            cook_time_minutes=10,
            servings=1,
            group_id=1,
            ingredients=[{"name": "Ingredient"} for _ in range(101)]
        )
    assert "at most 100 items" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        RecipeCreate(
            title="Test",
            prep_time_minutes=10,
            cook_time_minutes=10,
            servings=1,
            group_id=1,
            steps=[{"step_number": i, "instruction": "Step"} for i in range(101)]
        )
    assert "at most 100 items" in str(exc.value)


def test_governance_limits():
    """Test ProposalCreate list input limits."""
    with pytest.raises(ValidationError) as exc:
        ProposalCreate(
            title="Test",
            type="GENERAL",
            strategy="SIMPLE_MAJORITY",
            group_id=1,
            ballot_options=[{"text": "Option"} for _ in range(101)]
        )
    assert "at most 100 items" in str(exc.value)


def test_calendar_limits():
    """Test CalendarEventCreate list input limits."""
    with pytest.raises(ValidationError) as exc:
        CalendarEventCreate(
            title="Test",
            event_date="2024-01-01T00:00:00Z",
            category="OTHER",
            group_id=1,
            attendee_ids=[1] * 101
        )
    assert "at most 100 items" in str(exc.value)


def test_comment_limits():
    """Test CommentCreate list input limits."""
    with pytest.raises(ValidationError) as exc:
        CommentCreate(
            parent_id=1,
            parent_type="EXPENSE",
            content="Test",
            mentioned_user_ids=[1] * 101
        )
    assert "at most 100 items" in str(exc.value)
