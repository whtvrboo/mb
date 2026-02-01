import base64

import pytest
from cryptography.fernet import InvalidToken

from mitlist.modules.documents.service import _decrypt_password, _encrypt_password


def test_encryption_implementation():
    """Test that encryption uses Fernet and decryption handles both formats."""
    password = "super_secret_password_123"

    # Test 1: Encryption should produce a Fernet token (not just base64)
    encrypted = _encrypt_password(password)

    # Base64 of this password would be 'c3VwZXJfc2VjcmV0X3Bhc3N3b3JkXzEyMw=='
    # Fernet tokens are longer and typically start with 'gAAAA' (version 128)
    assert len(encrypted) > 50
    assert encrypted != base64.b64encode(password.encode()).decode()
    # assert encrypted.startswith("gAAAA")
    # Fernet tokens usually start with this but depends on timestamp

    # Test 2: Decryption should work for the new format
    decrypted = _decrypt_password(encrypted)
    assert decrypted == password

def test_legacy_backward_compatibility():
    """Test that we can still decrypt legacy Base64 passwords."""
    password = "legacy_password"
    legacy_encrypted = base64.b64encode(password.encode()).decode()

    # This should work via fallback mechanism
    decrypted = _decrypt_password(legacy_encrypted)
    assert decrypted == password

def test_corrupted_fernet_token():
    """Test that a corrupted Fernet token raises an error instead of returning garbage."""
    password = "test"
    encrypted = _encrypt_password(password)

    # Corrupt the token (keep length same, change characters)
    # Ensure we keep the "gAAAA" prefix intact so it's treated as Fernet
    # encrypted is likely > 50 chars
    corrupted = encrypted[:5] + "AAAA" + encrypted[9:]

    # New behavior: Must raise an exception (InvalidToken), NOT fall back to base64
    # and return garbage bytes.
    with pytest.raises(InvalidToken):
        _decrypt_password(corrupted)
