"""
Lists module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
Never import models or service directly from other modules.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from mitlist.modules.lists import models, schemas, service

# Re-export schemas (public)
__all__ = [
    "ListResponse",
    "ListCreate",
    "ListUpdate",
    "ItemResponse",
    "ItemCreate",
    "ItemUpdate",
    "get_list_by_id",
    "create_list",
    "update_list",
]

# Re-export schemas
ListResponse = schemas.ListResponse
ListCreate = schemas.ListCreate
ListUpdate = schemas.ListUpdate
ItemResponse = schemas.ItemResponse
ItemCreate = schemas.ItemCreate
ItemUpdate = schemas.ItemUpdate

# Re-export service functions (public API)
get_list_by_id = service.get_list_by_id
create_list = service.create_list
update_list = service.update_list
