from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# Import the service module to test
from mitlist.modules.documents import service


@pytest.mark.asyncio
async def test_delete_document_success():
    """
    Test that delete_document works correctly and sets deleted_at.
    """
    # Mock DB session
    db = AsyncMock(spec=AsyncSession)

    # Mock get_document_by_id to return a mock document
    mock_doc = MagicMock()
    # Ensure deleted_at is initially None
    mock_doc.deleted_at = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc
    db.execute.return_value = mock_result

    await service.delete_document(db, 1)

    # Verify deleted_at was set
    assert mock_doc.deleted_at is not None
    # Verify it was set to a timezone-aware datetime
    assert mock_doc.deleted_at.tzinfo is not None

    # Verify db.flush was called
    db.flush.assert_called_once()
