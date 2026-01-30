import type {
  UserResponse,
  UserUpdate,
  GroupResponse,
  GroupCreate,
  GroupUpdate,
  GroupMemberResponse,
  UserGroupResponse,
  UserGroupUpdate,
  UserGroupCreate,
  InviteResponse,
  InviteCreateRequest,
  InviteAcceptRequest,
  LocationResponse,
  LocationCreate,
  LocationUpdate,
  ServiceContactResponse,
  ServiceContactCreate,
  ServiceContactUpdate,
} from '~/types/auth'

export function useAuth() {
  const $api = useNuxtApp().$api
  const groupId = useCurrentGroupId()

  return {
    // --- Users ---
    getMe: () => useApi<UserResponse>('/users/me'),
    updateMe: (data: UserUpdate) =>
      $api<UserResponse>('/users/me', { method: 'PATCH', body: data }),
    deleteMe: () => $api<void>('/users/me', { method: 'DELETE' }),

    // --- Groups ---
    listGroups: () => useApi<GroupResponse[]>('/groups'),
    getGroup: (groupIdParam: number) =>
      useApi<GroupResponse>(`/groups/${groupIdParam}`),
    createGroup: (data: GroupCreate) =>
      $api<GroupResponse>('/groups', { method: 'POST', body: data }),
    updateGroup: (groupIdParam: number, data: GroupUpdate) =>
      $api<GroupResponse>(`/groups/${groupIdParam}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteGroup: (groupIdParam: number) =>
      $api<void>(`/groups/${groupIdParam}`, { method: 'DELETE' }),

    // --- Group members ---
    listGroupMembers: (groupIdParam: number) =>
      useApi<GroupMemberResponse[]>(`/groups/${groupIdParam}/members`),
    addGroupMember: (groupIdParam: number, data: UserGroupCreate) =>
      $api<UserGroupResponse>(`/groups/${groupIdParam}/members`, {
        method: 'POST',
        body: data,
      }),
    updateGroupMember: (
      groupIdParam: number,
      userId: number,
      data: UserGroupUpdate,
    ) =>
      $api<UserGroupResponse>(
        `/groups/${groupIdParam}/members/${userId}`,
        { method: 'PATCH', body: data },
      ),
    removeGroupMember: (groupIdParam: number, userId: number) =>
      $api<void>(`/groups/${groupIdParam}/members/${userId}`, {
        method: 'DELETE',
      }),
    leaveGroup: (groupIdParam: number) =>
      $api<void>(`/groups/${groupIdParam}/leave`, { method: 'POST' }),

    // --- Invites ---
    getInviteByCode: (code: string) =>
      useApi<InviteResponse>(`/invites/${encodeURIComponent(code)}`),
    joinByInvite: (data: InviteAcceptRequest) =>
      $api<UserGroupResponse>('/invites/join', { method: 'POST', body: data }),
    createInvite: (groupIdParam: number, data: InviteCreateRequest) =>
      $api<InviteResponse>(`/groups/${groupIdParam}/invites`, {
        method: 'POST',
        body: data,
      }),
    listGroupInvites: (groupIdParam: number) =>
      useApi<InviteResponse[]>(`/groups/${groupIdParam}/invites`),
    revokeInvite: (inviteId: number) =>
      $api<void>(`/invites/${inviteId}`, { method: 'DELETE' }),

    // --- Locations (require group_id query) ---
    listLocations: (groupIdParam: number) =>
      useApi<LocationResponse[]>('/locations', {
        query: { group_id: groupIdParam },
      }),
    getLocation: (locationId: number) =>
      useApi<LocationResponse>(`/locations/${locationId}`),
    createLocation: (data: LocationCreate) =>
      $api<LocationResponse>('/locations', { method: 'POST', body: data }),
    updateLocation: (locationId: number, data: LocationUpdate) =>
      $api<LocationResponse>(`/locations/${locationId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteLocation: (locationId: number) =>
      $api<void>(`/locations/${locationId}`, { method: 'DELETE' }),

    // --- Service contacts ---
    listServiceContacts: (groupIdParam: number) =>
      useApi<ServiceContactResponse[]>('/service-contacts', {
        query: { group_id: groupIdParam },
      }),
    getServiceContact: (contactId: number) =>
      useApi<ServiceContactResponse>(`/service-contacts/${contactId}`),
    createServiceContact: (data: ServiceContactCreate) =>
      $api<ServiceContactResponse>('/service-contacts', {
        method: 'POST',
        body: data,
      }),
    updateServiceContact: (
      contactId: number,
      data: ServiceContactUpdate,
    ) =>
      $api<ServiceContactResponse>(`/service-contacts/${contactId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteServiceContact: (contactId: number) =>
      $api<void>(`/service-contacts/${contactId}`, { method: 'DELETE' }),

    // Expose current group id ref for components
    groupId,
  }
}
