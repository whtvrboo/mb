"""Core validation utilities."""

from typing import Any


def validate_dict_size(
    value: dict[str, Any] | None,
    max_items: int = 50,
    max_key_length: int = 64,
    max_value_length: int = 255,
) -> dict[str, Any] | None:
    """
    Validate dictionary size limits to prevent DoS.

    Checks:
    - Number of items <= max_items
    - Key length <= max_key_length
    - Value string representation length <= max_value_length (for simple types)
    """
    if value is None:
        return value

    if len(value) > max_items:
        raise ValueError(f"Too many items in dictionary (max {max_items})")

    for k, v in value.items():
        if len(str(k)) > max_key_length:
            raise ValueError(f"Key too long: {k[:20]}... (max {max_key_length} chars)")

        # Only check value length for simple types, complex types might need different handling
        # For now, we stringify and check length which is a safe default for tags/metadata
        if v is not None:
            v_str = str(v)
            if len(v_str) > max_value_length:
                raise ValueError(
                    f"Value too long for key {k}: {v_str[:20]}... (max {max_value_length} chars)"
                )

    return value
