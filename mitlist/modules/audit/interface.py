"""
Audit module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
Never import models or service directly from other modules.
"""

from mitlist.modules.audit import schemas, service

__all__ = [
    "schemas",
    # Audit Logs
    "log_action",
    "list_audit_logs",
    "get_entity_history",
    # Reports
    "generate_report",
    "list_reports",
    "get_report_by_id",
    # Tags
    "list_tags",
    "get_tag_by_id",
    "create_tag",
    "update_tag",
    "delete_tag",
    # Tag Assignments
    "assign_tag",
    "remove_tag_assignment",
    "get_entity_tags",
    # Admin
    "get_system_stats",
    "broadcast_notification",
]

log_action = service.log_action
list_audit_logs = service.list_audit_logs
get_entity_history = service.get_entity_history

generate_report = service.generate_report
list_reports = service.list_reports
get_report_by_id = service.get_report_by_id

list_tags = service.list_tags
get_tag_by_id = service.get_tag_by_id
create_tag = service.create_tag
update_tag = service.update_tag
delete_tag = service.delete_tag

assign_tag = service.assign_tag
remove_tag_assignment = service.remove_tag_assignment
get_entity_tags = service.get_entity_tags

get_system_stats = service.get_system_stats
broadcast_notification = service.broadcast_notification
