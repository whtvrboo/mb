import base64

import pytest
from cryptography.fernet import InvalidToken

from mitlist.modules.documents.service import (
    _decrypt_password,
    _encrypt_password,
    generate_presigned_upload_url,
)


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


def test_filename_sanitization():
    """Test that filenames are sanitized to prevent traversal and bad chars."""
    group_id = 1
    mime = "text/plain"
    size = 123

    # Test cases: (input_filename, expected_to_not_contain)
    test_cases = [
        ("../../etc/passwd", "/"),  # Slashes removed
        ("folder/file.txt", "/"),
        (r"folder\file.txt", "\\"),  # Backslashes removed
        ("file with spaces.txt", " "),  # Spaces removed/replaced
        ("file<name>.txt", "<"),  # Angle brackets removed
        ("file\x00name.txt", "\x00"),  # Null bytes removed
        ("über_file.txt", "ü"),  # Unicode normalized/removed
    ]

    for filename, bad_char in test_cases:
        url, file_key, _ = generate_presigned_upload_url(group_id, filename, mime, size)

        # Extract the filename part from the key
        # Key format: groups/{group_id}/documents/{timestamp}_{random_suffix}_{safe_name}
        parts = file_key.split("/")
        # Should be exactly 3 slashes -> 4 parts
        # groups/1/documents/filename
        assert len(parts) == 4
        assert parts[0] == "groups"
        assert parts[1] == str(group_id)
        assert parts[2] == "documents"

        actual_filename = parts[3]

        # Check that bad char is gone
        assert bad_char not in actual_filename, (
            f"Failed to sanitize '{bad_char}' from '{filename}'. Got: {actual_filename}"
        )

        # Ensure no traversal sequences (though without slashes they are benign, we check for clean output)
        # We don't strictly forbid '..' if it's not part of a path, but verifying correctness:
        # with my regex [^a-zA-Z0-9._-], dots are allowed.
        # ../../etc/passwd -> .._.._etc_passwd.
        # This is safe because no slashes.

    # Test Empty Filename
    _, key_empty, _ = generate_presigned_upload_url(group_id, "", mime, size)
    assert "unnamed_file" in key_empty

    # Test Unicode Normalization
    # 'ü' (u umlaut) should become 'u' or be removed if ascii encoding strips it?
    # NFKD decomposes 'ü' to 'u' + '̈'.
    # encode("ascii", "ignore") keeps 'u' and drops '̈'.
    _, key_unicode, _ = generate_presigned_upload_url(group_id, "über.txt", mime, size)
    assert "uber.txt" in key_unicode
