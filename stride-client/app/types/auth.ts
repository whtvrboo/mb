/** Auth module types: User, Group, Invite, Location, ServiceContact */

export interface UserResponse {
  id: number
  email: string
  name: string
  phone_number: string | null
  birth_date: string | null
  avatar_url: string | null
  language_code: string
  is_superuser: boolean
  is_active: boolean
  preferences: Record<string, unknown> | null
  last_login_at: string | null
  created_at: string
  updated_at: string
}

export interface UserUpdate {
  name?: string
  phone_number?: string | null
  birth_date?: string | null
  avatar_url?: string | null
  language_code?: string | null
  preferences?: Record<string, unknown> | null
}

export interface UserLoginRequest {
  email: string
  password: string
}

export interface UserLoginResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

export interface GroupResponse {
  id: number
  name: string
  default_currency: string
  timezone: string
  description: string | null
  avatar_url: string | null
  address: string | null
  created_by_id: number
  lease_start_date: string | null
  lease_end_date: string | null
  landlord_contact_id: number | null
  created_at: string
  updated_at: string
}

export interface GroupCreate {
  name: string
  default_currency?: string
  timezone?: string
  description?: string | null
  avatar_url?: string | null
  address?: string | null
  lease_start_date?: string | null
  lease_end_date?: string | null
}

export interface GroupUpdate {
  name?: string | null
  default_currency?: string | null
  timezone?: string | null
  description?: string | null
  avatar_url?: string | null
  address?: string | null
  lease_start_date?: string | null
  lease_end_date?: string | null
  landlord_contact_id?: number | null
}

export interface GroupMemberResponse {
  id: number
  user_id: number
  role: string
  nickname: string | null
  joined_at: string
  user: UserResponse
}

export interface UserGroupResponse {
  id: number
  user_id: number
  group_id: number
  role: string
  nickname: string | null
  joined_at: string
  left_at: string | null
  created_at: string
  updated_at: string
}

export interface UserGroupUpdate {
  role?: string
  nickname?: string | null
}

export interface UserGroupCreate {
  user_id: number
  role?: string
}

export interface InviteResponse {
  id: number
  group_id: number
  code: string
  email_hint: string | null
  role: string
  max_uses: number
  use_count: number
  expires_at: string | null
  is_active: boolean
  created_by_id: number
  created_at: string
  updated_at: string
}

export interface InviteCreateRequest {
  role: string
  email_hint?: string | null
  max_uses?: number
  expires_at?: string | null
}

export interface InviteAcceptRequest {
  code: string
}

export interface LocationResponse {
  id: number
  group_id: number
  name: string
  floor_level: string | null
  sunlight_direction: string | null
  humidity_level: string | null
  temperature_avg_celsius: number | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface LocationCreate {
  group_id: number
  name: string
  floor_level?: string | null
  sunlight_direction?: string | null
  humidity_level?: string | null
  temperature_avg_celsius?: number | null
  notes?: string | null
}

export interface LocationUpdate {
  name?: string | null
  floor_level?: string | null
  sunlight_direction?: string | null
  humidity_level?: string | null
  temperature_avg_celsius?: number | null
  notes?: string | null
}

export interface ServiceContactResponse {
  id: number
  group_id: number
  name: string
  job_title: string | null
  company_name: string | null
  phone: string | null
  email: string | null
  address: string | null
  website_url: string | null
  emergency_contact: boolean
  notes: string | null
  created_at: string
  updated_at: string
}

export interface ServiceContactCreate {
  group_id: number
  name: string
  job_title?: string | null
  company_name?: string | null
  phone?: string | null
  email?: string | null
  address?: string | null
  website_url?: string | null
  emergency_contact?: boolean
  notes?: string | null
}

export interface ServiceContactUpdate {
  name?: string | null
  job_title?: string | null
  company_name?: string | null
  phone?: string | null
  email?: string | null
  address?: string | null
  website_url?: string | null
  emergency_contact?: boolean
  notes?: string | null
}
