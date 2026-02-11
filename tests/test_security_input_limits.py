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
