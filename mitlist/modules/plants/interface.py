"""
Plants module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
"""

from mitlist.modules.plants import schemas, service

__all__ = [
    "schemas",
    "list_species",
    "get_species_by_id",
    "create_species",
    "list_plants",
    "get_plant_by_id",
    "create_plant",
    "update_plant",
    "mark_plant_dead",
    "list_plant_logs",
    "create_plant_log",
    "get_schedule_by_id",
    "list_plant_schedules",
    "create_schedule",
    "mark_schedule_done",
    "get_overdue_schedules",
]

list_species = service.list_species
get_species_by_id = service.get_species_by_id
create_species = service.create_species

list_plants = service.list_plants
get_plant_by_id = service.get_plant_by_id
create_plant = service.create_plant
update_plant = service.update_plant
mark_plant_dead = service.mark_plant_dead

list_plant_logs = service.list_plant_logs
create_plant_log = service.create_plant_log

get_schedule_by_id = service.get_schedule_by_id
list_plant_schedules = service.list_plant_schedules
create_schedule = service.create_schedule
mark_schedule_done = service.mark_schedule_done
get_overdue_schedules = service.get_overdue_schedules
