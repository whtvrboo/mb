/** Pets module types: Pet, PetMedicalRecord, PetSchedule, PetLog */

export interface PetResponse {
  id: number
  group_id: number
  name: string
  species: string
  breed: string | null
  sex: string | null
  date_of_birth: string | null
  adoption_date: string | null
  chip_id: string | null
  weight_kg: number | null
  color_markings: string | null
  photo_url: string | null
  vet_contact_id: number | null
  insurance_policy_number: string | null
  insurance_provider: string | null
  medication_schedule: string | null
  diet_instructions: string | null
  special_needs: string | null
  is_alive: boolean
  died_at: string | null
  created_at: string
  updated_at: string
}

export interface PetCreate {
  group_id: number
  name: string
  species: string
  breed?: string | null
  sex?: string | null
  date_of_birth?: string | null
  adoption_date?: string | null
  chip_id?: string | null
  weight_kg?: number | null
  color_markings?: string | null
  photo_url?: string | null
  vet_contact_id?: number | null
  insurance_policy_number?: string | null
  insurance_provider?: string | null
  diet_instructions?: string | null
  medication_schedule?: string | null
  special_needs?: string | null
}

export interface PetUpdate {
  name?: string | null
  breed?: string | null
  sex?: string | null
  date_of_birth?: string | null
  chip_id?: string | null
  weight_kg?: number | null
  color_markings?: string | null
  photo_url?: string | null
  vet_contact_id?: number | null
  insurance_policy_number?: string | null
  insurance_provider?: string | null
  diet_instructions?: string | null
  medication_schedule?: string | null
  special_needs?: string | null
}

export interface PetMarkDeceasedRequest {
  died_at: string
}

export interface PetMedicalRecordResponse {
  id: number
  pet_id: number
  type: string
  description: string | null
  performed_at: string | null
  performed_by: string | null
  expires_at: string | null
  reminder_days_before: number | null
  notes: string | null
  cost_expense_id: number | null
  document_id: number | null
  created_at: string
  updated_at: string
}

export interface PetMedicalRecordCreate {
  pet_id: number
  type: string
  description?: string | null
  performed_at?: string | null
  performed_by?: string | null
  expires_at?: string | null
  reminder_days_before?: number | null
  notes?: string | null
  cost_expense_id?: number | null
  document_id?: number | null
}

export interface PetLogResponse {
  id: number
  pet_id: number
  user_id: number
  action: string
  value_amount: number | null
  value_unit: string | null
  notes: string | null
  photo_url: string | null
  occurred_at: string
  created_at: string
  updated_at: string
}

export interface PetLogCreate {
  action: string
  occurred_at?: string
  value_amount?: number | null
  value_unit?: string | null
  notes?: string | null
  photo_url?: string | null
}

export interface PetScheduleResponse {
  id: number
  pet_id: number
  action_type: string
  frequency_type: string
  time_of_day: string | null
  assigned_to_id: number | null
  is_rotating: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PetScheduleCreate {
  action_type: string
  frequency_type: string
  time_of_day?: string | null
  assigned_to_id?: number | null
  is_rotating?: boolean
}

export interface PetScheduleMarkDoneRequest {
  notes?: string | null
  value_amount?: number | null
  value_unit?: string | null
}
