"""
Security tests for input validation.
"""

import pytest
from pydantic import ValidationError

from mitlist.core.validation import validate_dict_size
from mitlist.modules.auth.schemas import UserUpdate


def test_validate_dict_size_basic():
    """Test basic dictionary size validation."""
    data = {"a": 1, "b": 2}
    assert validate_dict_size(data, max_items=2) == data

    with pytest.raises(ValueError, match="Dictionary exceeds maximum items"):
        validate_dict_size({"a": 1, "b": 2, "c": 3}, max_items=2)


def test_validate_dict_size_key_length():
    """Test key length validation."""
    data = {"short": 1}
    assert validate_dict_size(data, max_key_length=5) == data

    with pytest.raises(ValueError, match="Key length exceeds maximum"):
        validate_dict_size({"toolong": 1}, max_key_length=5)


def test_validate_dict_size_value_length():
    """Test value length validation."""
    data = {"a": "short"}
    assert validate_dict_size(data, max_value_length=5) == data

    with pytest.raises(ValueError, match="Value length exceeds maximum"):
        validate_dict_size({"a": "toolong"}, max_value_length=5)

    # Non-string values should be ignored by the length check (or handled gracefully)
    data_int = {"a": 123456}
    assert validate_dict_size(data_int, max_value_length=5) == data_int


def test_validate_dict_size_recursion():
    """Test recursion limit."""
    # Valid recursion
    data = {"a": {"b": {"c": 1}}}
    assert validate_dict_size(data, max_depth=3) == data

    # Too deep
    data_deep = {"a": {"b": {"c": {"d": 1}}}}
    with pytest.raises(ValueError, match="Recursion depth exceeds maximum"):
        validate_dict_size(data_deep, max_depth=2)


def test_user_update_preferences_validation():
    """Test UserUpdate schema validation for preferences."""
    # Valid preferences
    valid_prefs = {"theme": "dark", "notifications": True}
    user = UserUpdate(preferences=valid_prefs)
    assert user.preferences == valid_prefs

    # Too many items
    many_items = {str(i): i for i in range(51)}
    with pytest.raises(ValidationError) as excinfo:
        UserUpdate(preferences=many_items)
    assert "Dictionary exceeds maximum items (50)" in str(excinfo.value)

    # Key too long
    long_key = {"a" * 101: "value"}
    with pytest.raises(ValidationError) as excinfo:
        UserUpdate(preferences=long_key)
    assert "Key length exceeds maximum (100)" in str(excinfo.value)

    # Value too long
    long_value = {"key": "a" * 1001}
    with pytest.raises(ValidationError) as excinfo:
        UserUpdate(preferences=long_value)
    assert "Value length exceeds maximum (1000)" in str(excinfo.value)

    # Recursion check in preferences (default max_depth=5)
    deep_prefs = {"a": {"b": {"c": {"d": {"e": {"f": {"g": 1}}}}}}}
    with pytest.raises(ValidationError) as excinfo:
        UserUpdate(preferences=deep_prefs)
    assert "Recursion depth exceeds maximum (5)" in str(excinfo.value)
