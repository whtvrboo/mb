"""
Auth module PUBLIC interface.

Other modules may ONLY import from this file (and schemas.py).
Never import models or service directly from other modules.
"""

from mitlist.modules.auth import schemas, service

__all__ = [
    "schemas",
    # Users
    "get_user_by_id",
    "update_user",
    "soft_delete_user",
    # Groups
    "list_groups_for_user",
    "create_group",
    "get_group_by_id",
    "update_group",
    "soft_delete_group",
    "list_group_members",
    "update_member",
    "remove_member",
    "leave_group",
    "require_member",
    "require_admin",
    # Invites
    "create_invite",
    "get_invite_by_id",
    "get_invite_by_code",
    "require_valid_invite",
    "accept_invite",
    "revoke_invite",
    "list_invites_for_group",
    # Members
    "add_member",
    # Locations
    "list_locations",
    "get_location_by_id",
    "create_location",
    "update_location",
    "delete_location",
    # Service Contacts
    "list_service_contacts",
    "get_service_contact_by_id",
    "create_service_contact",
    "update_service_contact",
    "delete_service_contact",
]

get_user_by_id = service.get_user_by_id
update_user = service.update_user
soft_delete_user = service.soft_delete_user

list_groups_for_user = service.list_groups_for_user
create_group = service.create_group
get_group_by_id = service.get_group_by_id
update_group = service.update_group
soft_delete_group = service.soft_delete_group
list_group_members = service.list_group_members
update_member = service.update_member
remove_member = service.remove_member
leave_group = service.leave_group
require_member = service.require_member
require_admin = service.require_admin

create_invite = service.create_invite
get_invite_by_id = service.get_invite_by_id
get_invite_by_code = service.get_invite_by_code
require_valid_invite = service.require_valid_invite
accept_invite = service.accept_invite
revoke_invite = service.revoke_invite
list_invites_for_group = service.list_invites_for_group

add_member = service.add_member

list_locations = service.list_locations
get_location_by_id = service.get_location_by_id
create_location = service.create_location
update_location = service.update_location
delete_location = service.delete_location

list_service_contacts = service.list_service_contacts
get_service_contact_by_id = service.get_service_contact_by_id
create_service_contact = service.create_service_contact
update_service_contact = service.update_service_contact
delete_service_contact = service.delete_service_contact
