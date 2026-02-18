"""
Common validation utilities.
"""

from typing import Any


def validate_dict_size(
    v: dict[str, Any] | None,
    max_items: int = 50,
    max_key_length: int = 100,
    max_value_length: int = 1000,
    max_depth: int = 5,
    _current_depth: int = 0,
) -> dict[str, Any] | None:
    """
    Validate that a dictionary does not exceed size limits.

    Args:
        v: The dictionary to validate.
        max_items: Maximum number of items allowed.
        max_key_length: Maximum length of keys.
        max_value_length: Maximum length of string values.
        max_depth: Maximum recursion depth for nested dictionaries.

    Raises:
        ValueError: If limits are exceeded.

    Returns:
        The validated dictionary.
    """
    if v is None:
        return v

    if _current_depth > max_depth:
        raise ValueError(f"Recursion depth exceeds maximum ({max_depth})")

    if len(v) > max_items:
        raise ValueError(f"Dictionary exceeds maximum items ({max_items})")

    for key, value in v.items():
        if len(str(key)) > max_key_length:
            raise ValueError(f"Key length exceeds maximum ({max_key_length})")

        if isinstance(value, dict):
            validate_dict_size(
                value,
                max_items=max_items,
                max_key_length=max_key_length,
                max_value_length=max_value_length,
                max_depth=max_depth,
                _current_depth=_current_depth + 1,
            )
        elif isinstance(value, str) and len(value) > max_value_length:
            raise ValueError(f"Value length exceeds maximum ({max_value_length})")

    return v
