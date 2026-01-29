"""
Chores module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
"""

from mitlist.modules.chores import schemas, service

__all__ = [
    "schemas",
    "list_chores",
    "get_chore_by_id",
    "create_chore",
    "update_chore",
    "delete_chore",
    "list_assignments",
    "get_assignment_by_id",
    "complete_assignment",
    "skip_assignment",
    "reassign_assignment",
    "list_chore_history",
]

list_chores = service.list_chores
get_chore_by_id = service.get_chore_by_id
create_chore = service.create_chore
update_chore = service.update_chore
delete_chore = service.delete_chore
list_assignments = service.list_assignments
get_assignment_by_id = service.get_assignment_by_id
complete_assignment = service.complete_assignment
skip_assignment = service.skip_assignment
reassign_assignment = service.reassign_assignment
list_chore_history = service.list_chore_history
