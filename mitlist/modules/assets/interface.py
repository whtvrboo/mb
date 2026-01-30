"""
Assets module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
"""

from mitlist.modules.assets import schemas, service

__all__ = [
    "schemas",
    "list_assets",
    "get_asset",
    "create_asset",
    "update_asset",
    "dispose_asset",
    "get_maintenance_task",
    "list_maintenance_tasks",
    "create_maintenance_task",
    "update_maintenance_task",
    "list_maintenance_logs",
    "create_maintenance_log",
    "get_insurance_by_id",
    "list_insurances",
    "create_insurance",
    "update_insurance",
]

list_assets = service.list_assets
get_asset = service.get_asset
create_asset = service.create_asset
update_asset = service.update_asset
dispose_asset = service.dispose_asset

get_maintenance_task = service.get_maintenance_task
list_maintenance_tasks = service.list_maintenance_tasks
create_maintenance_task = service.create_maintenance_task
update_maintenance_task = service.update_maintenance_task

list_maintenance_logs = service.list_maintenance_logs
create_maintenance_log = service.create_maintenance_log

get_insurance_by_id = service.get_insurance_by_id
list_insurances = service.list_insurances
create_insurance = service.create_insurance
update_insurance = service.update_insurance
