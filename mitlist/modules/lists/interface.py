"""
Lists module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
Never import models or service directly from other modules.
"""

from mitlist.modules.lists import schemas, service

# Re-export schemas (public)
__all__ = [
    "ListResponse",
    "ListCreate",
    "ListUpdate",
    "ItemResponse",
    "ItemCreate",
    "ItemUpdate",
    "ItemBulkCreate",
    "ItemBulkResponse",
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItemResponse",
    "list_lists",
    "get_list_by_id",
    "create_list",
    "update_list",
    "get_items_by_list_id",
    "get_item_by_id",
    "create_item",
    "update_item",
    "delete_item",
    "bulk_add_items",
    "list_inventory",
    "get_inventory_item_by_id",
    "update_inventory_item",
]

# Re-export schemas
ListResponse = schemas.ListResponse
ListCreate = schemas.ListCreate
ListUpdate = schemas.ListUpdate
ItemResponse = schemas.ItemResponse
ItemCreate = schemas.ItemCreate
ItemUpdate = schemas.ItemUpdate
ItemBulkCreate = schemas.ItemBulkCreate
ItemBulkResponse = schemas.ItemBulkResponse
InventoryItemCreate = schemas.InventoryItemCreate
InventoryItemUpdate = schemas.InventoryItemUpdate
InventoryItemResponse = schemas.InventoryItemResponse

# Re-export service functions (public API)
list_lists = service.list_lists
get_list_by_id = service.get_list_by_id
create_list = service.create_list
update_list = service.update_list
get_items_by_list_id = service.get_items_by_list_id
get_item_by_id = service.get_item_by_id
create_item = service.create_item
update_item = service.update_item
delete_item = service.delete_item
bulk_add_items = service.bulk_add_items
list_inventory = service.list_inventory
get_inventory_item_by_id = service.get_inventory_item_by_id
update_inventory_item = service.update_inventory_item
