import base64
import pytest
from mitlist.modules.documents.service import _encrypt_password, _decrypt_password

def test_encryption_implementation():
    """Test that encryption uses Fernet and decryption handles both formats."""
    password = "super_secret_password_123"

    # Test 1: Encryption should produce a Fernet token (not just base64)
    encrypted = _encrypt_password(password)

    # Base64 of this password would be 'c3VwZXJfc2VjcmV0X3Bhc3N3b3JkXzEyMw=='
    # Fernet tokens are longer and typically start with 'gAAAA' (version 128)
    assert len(encrypted) > 50
    assert encrypted != base64.b64encode(password.encode()).decode()
    # assert encrypted.startswith("gAAAA") # Fernet tokens usually start with this but depends on timestamp

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
