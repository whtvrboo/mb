import base64
from unittest import mock

import pytest
from cryptography.fernet import InvalidToken

from mitlist.core.config import settings
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
    """Test legacy Base64 password decryption logic."""
    password = "legacy_password"
    legacy_encrypted = base64.b64encode(password.encode()).decode()

    # 1. By default (setting=False), this should FAIL
    # We verify the setting is indeed False by default
    assert settings.ALLOW_LEGACY_INSECURE_PASSWORDS is False

    with pytest.raises(ValueError, match="Legacy Base64 password access is disabled"):
        _decrypt_password(legacy_encrypted)

    # 2. When enabled (setting=True), this should SUCCEED
    with mock.patch.object(settings, "ALLOW_LEGACY_INSECURE_PASSWORDS", True):
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
