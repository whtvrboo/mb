"""
Pets module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
"""

from mitlist.modules.pets import schemas, service

__all__ = [
    "schemas",
    "list_pets",
    "get_pet_by_id",
    "create_pet",
    "update_pet",
    "mark_pet_deceased",
    "list_medical_records",
    "create_medical_record",
    "get_expiring_vaccines",
    "list_pet_logs",
    "create_pet_log",
    "get_schedule_by_id",
    "list_pet_schedules",
    "create_pet_schedule",
    "mark_schedule_done",
]

list_pets = service.list_pets
get_pet_by_id = service.get_pet_by_id
create_pet = service.create_pet
update_pet = service.update_pet
mark_pet_deceased = service.mark_pet_deceased

list_medical_records = service.list_medical_records
create_medical_record = service.create_medical_record
get_expiring_vaccines = service.get_expiring_vaccines

list_pet_logs = service.list_pet_logs
create_pet_log = service.create_pet_log

get_schedule_by_id = service.get_schedule_by_id
list_pet_schedules = service.list_pet_schedules
create_pet_schedule = service.create_pet_schedule
mark_schedule_done = service.mark_schedule_done
