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
    # Dependencies
    "add_dependency",
    "remove_dependency",
    "get_dependencies",
    "check_dependencies_met",
    # Templates
    "list_templates",
    "create_template",
    "create_chore_from_template",
    # Stats
    "get_group_stats",
    "get_user_stats",
    "get_leaderboard",
    # Actions
    "start_assignment",
    "rate_assignment",
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

# Dependencies
add_dependency = service.add_dependency
remove_dependency = service.remove_dependency
get_dependencies = service.get_dependencies
check_dependencies_met = service.check_dependencies_met

# Templates
list_templates = service.list_templates
create_template = service.create_template
create_chore_from_template = service.create_chore_from_template

# Stats
get_group_stats = service.get_group_stats
get_user_stats = service.get_user_stats
get_leaderboard = service.get_leaderboard

# Actions
start_assignment = service.start_assignment
rate_assignment = service.rate_assignment
