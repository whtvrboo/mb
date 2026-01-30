/** Plants module types: Plant, PlantSpecies, PlantSchedule, PlantLog */

export interface PlantSpeciesResponse {
  id: number
  scientific_name: string
  common_name: string | null
  toxicity: string | null
  light_needs: string | null
  water_interval_summer: number | null
  water_interval_winter: number | null
  humidity_preference: string | null
  fertilize_frequency_weeks: number | null
  growth_rate: string | null
  mature_height_cm: number | null
  propagation_method: string | null
  care_difficulty: string | null
  created_at: string
  updated_at: string
}

export interface PlantResponse {
  id: number
  group_id: number
  species_id: number
  location_id: number | null
  nickname: string | null
  acquired_at: string | null
  acquired_from: string | null
  pot_size_cm: number | null
  photo_url: string | null
  notes: string | null
  parent_plant_id: number | null
  is_alive: boolean
  died_at: string | null
  death_reason: string | null
  created_at: string
  updated_at: string
}

export interface PlantWithSpeciesResponse extends PlantResponse {
  species: PlantSpeciesResponse
}

export interface PlantCreate {
  group_id: number
  species_id: number
  nickname?: string | null
  location_id?: number | null
  acquired_at?: string | null
  acquired_from?: string | null
  pot_size_cm?: number | null
  photo_url?: string | null
  notes?: string | null
  parent_plant_id?: number | null
}

export interface PlantUpdate {
  location_id?: number | null
  nickname?: string | null
  pot_size_cm?: number | null
  photo_url?: string | null
  notes?: string | null
}

export interface PlantMarkDeadRequest {
  death_reason?: string | null
}

export interface PlantLogResponse {
  id: number
  plant_id: number
  user_id: number
  action: string
  quantity_value: number | null
  quantity_unit: string | null
  notes: string | null
  photo_url: string | null
  occurred_at: string
  created_at: string
  updated_at: string
}

export interface PlantLogCreate {
  action: string
  occurred_at?: string
  quantity_value?: number | null
  quantity_unit?: string | null
  notes?: string | null
  photo_url?: string | null
}

export interface PlantScheduleResponse {
  id: number
  plant_id: number
  action_type: string
  next_due_date: string | null
  frequency_days: number | null
  assigned_to_id: number | null
  created_at: string
  updated_at: string
}

export interface PlantScheduleCreate {
  action_type: string
  frequency_days?: number | null
  next_due_date?: string | null
  assigned_to_id?: number | null
}

export interface PlantScheduleMarkDoneRequest {
  notes?: string | null
  quantity_value?: number | null
  quantity_unit?: string | null
}
