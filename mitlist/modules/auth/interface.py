"""
Auth module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
Never import models or service directly from other modules.
"""

from mitlist.modules.auth import schemas

__all__ = ["schemas"]
