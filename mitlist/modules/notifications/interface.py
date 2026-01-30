"""
Notifications module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
Never import models or service directly from other modules.
"""

from mitlist.modules.notifications import schemas, service

__all__ = [
    "schemas",
    # Notifications
    "list_notifications",
    "create_notification",
    "create_notifications_bulk",
    "get_notification_by_id",
    "mark_read",
    "mark_all_read",
    "get_unread_count",
    # Preferences
    "get_preferences",
    "get_preference",
    "update_preference",
    # Comments
    "list_comments",
    "get_comment_by_id",
    "create_comment",
    "update_comment",
    "delete_comment",
    # Reactions
    "get_reaction",
    "toggle_reaction",
    "list_reactions",
]

list_notifications = service.list_notifications
create_notification = service.create_notification
create_notifications_bulk = service.create_notifications_bulk
get_notification_by_id = service.get_notification_by_id
mark_read = service.mark_read
mark_all_read = service.mark_all_read
get_unread_count = service.get_unread_count

get_preferences = service.get_preferences
get_preference = service.get_preference
update_preference = service.update_preference

list_comments = service.list_comments
get_comment_by_id = service.get_comment_by_id
create_comment = service.create_comment
update_comment = service.update_comment
delete_comment = service.delete_comment

get_reaction = service.get_reaction
toggle_reaction = service.toggle_reaction
list_reactions = service.list_reactions
