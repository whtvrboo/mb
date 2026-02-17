import pytest
from pydantic import ValidationError
from decimal import Decimal

from mitlist.modules.auth.schemas import LocationBase, ServiceContactBase, InviteAcceptRequest, UserCreate, UserLoginRequest
from mitlist.modules.lists.schemas import ItemBase
from mitlist.modules.documents.schemas import SharedCredentialBase, DocumentSearchRequest, DocumentCreate, DocumentUpdate
from mitlist.modules.finance.schemas import ExpenseSplitInput

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

def test_document_tags_limits():
    """Test Document tags size limits."""
    huge_tags = {f"key_{i}": "val" for i in range(51)}

    # DocumentCreate (via DocumentBase)
    with pytest.raises(ValidationError) as exc:
        DocumentCreate(
            file_name="test.txt",
            mime_type="text/plain",
            group_id=1,
            file_key="key",
            file_size_bytes=100,
            tags=huge_tags
        )
    assert "Too many items in dictionary" in str(exc.value)

    # DocumentUpdate
    with pytest.raises(ValidationError) as exc:
        DocumentUpdate(tags=huge_tags)
    assert "Too many items in dictionary" in str(exc.value)

    # DocumentSearchRequest
    with pytest.raises(ValidationError) as exc:
        DocumentSearchRequest(group_id=1, tags=huge_tags)
    assert "Too many items in dictionary" in str(exc.value)

    # Key length limit
    long_key_tags = {"a" * 65: "val"}
    with pytest.raises(ValidationError) as exc:
        DocumentCreate(
            file_name="test.txt",
            mime_type="text/plain",
            group_id=1,
            file_key="key",
            file_size_bytes=100,
            tags=long_key_tags
        )
    assert "Key too long" in str(exc.value)

    # Value length limit
    long_val_tags = {"key": "a" * 256}
    with pytest.raises(ValidationError) as exc:
        DocumentCreate(
            file_name="test.txt",
            mime_type="text/plain",
            group_id=1,
            file_key="key",
            file_size_bytes=100,
            tags=long_val_tags
        )
    assert "Value too long" in str(exc.value)

def test_expense_split_manual_override_limits():
    """Test ExpenseSplitInput manual_override size limits."""
    huge_override = {f"key_{i}": "val" for i in range(21)}

    with pytest.raises(ValidationError) as exc:
        ExpenseSplitInput(
            user_id=1,
            owed_amount=Decimal("10.00"),
            manual_override=huge_override
        )
    assert "Too many items in dictionary" in str(exc.value)
