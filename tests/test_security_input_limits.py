import pytest
from pydantic import ValidationError

from mitlist.modules.auth.schemas import LocationBase, ServiceContactBase, InviteAcceptRequest, UserCreate, UserLoginRequest
from mitlist.modules.lists.schemas import ItemBase
from mitlist.modules.documents.schemas import SharedCredentialBase, DocumentSearchRequest
from mitlist.modules.recipes.schemas import RecipeCreate, GenerateShoppingListRequest, RecipeIngredientInput
from mitlist.modules.calendar.schemas import CalendarEventCreate
from mitlist.modules.governance.schemas import ProposalCreate, RankedVoteCreate, BallotOptionInput, RankedVoteInput
from mitlist.modules.audit.schemas import BulkTagAssignmentRequest

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

def test_recipe_create_ingredients_limit():
    """Test RecipeCreate ingredients max_length."""
    with pytest.raises(ValidationError) as exc:
        RecipeCreate(
            title="Test Recipe",
            prep_time_minutes=10,
            cook_time_minutes=10,
            servings=2,
            group_id=1,
            ingredients=[RecipeIngredientInput(name=f"Ing {i}") for i in range(101)]
        )
    assert "List should have at most 100 items" in str(exc.value)

def test_generate_shopping_list_request_limit():
    """Test GenerateShoppingListRequest meal_plan_ids max_length."""
    with pytest.raises(ValidationError) as exc:
        GenerateShoppingListRequest(meal_plan_ids=[i for i in range(101)])
    assert "List should have at most 100 items" in str(exc.value)

def test_calendar_event_create_attendees_limit():
    """Test CalendarEventCreate attendee_ids max_length."""
    from datetime import datetime
    with pytest.raises(ValidationError) as exc:
        CalendarEventCreate(
            title="Party",
            event_date=datetime.now(),
            category="SOCIAL",
            group_id=1,
            attendee_ids=[i for i in range(101)]
        )
    assert "List should have at most 100 items" in str(exc.value)

def test_proposal_create_options_limit():
    """Test ProposalCreate ballot_options max_length."""
    with pytest.raises(ValidationError) as exc:
        ProposalCreate(
            title="Big Vote",
            type="GENERAL",
            strategy="SIMPLE_MAJORITY",
            group_id=1,
            ballot_options=[BallotOptionInput(text=f"Option {i}") for i in range(51)]
        )
    assert "List should have at most 50 items" in str(exc.value)

def test_ranked_vote_create_choices_limit():
    """Test RankedVoteCreate ranked_choices max_length."""
    with pytest.raises(ValidationError) as exc:
        RankedVoteCreate(
            proposal_id=1,
            ranked_choices=[RankedVoteInput(ballot_option_id=i, rank=i) for i in range(1, 52)]
        )
    assert "List should have at most 50 items" in str(exc.value)

def test_bulk_tag_assignment_request_limit():
    """Test BulkTagAssignmentRequest tag_ids max_length."""
    with pytest.raises(ValidationError) as exc:
        BulkTagAssignmentRequest(
            entity_type="EXPENSE",
            entity_id=1,
            tag_ids=[i for i in range(51)]
        )
    assert "List should have at most 50 items" in str(exc.value)
