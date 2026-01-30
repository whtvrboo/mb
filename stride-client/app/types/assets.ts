/** Assets module types: HomeAsset, MaintenanceTask, MaintenanceLog, Insurance */

export interface HomeAssetResponse {
  id: number
  group_id: number
  name: string
  asset_type: string
  location_id: number | null
  brand: string | null
  model_number: string | null
  serial_number: string | null
  purchase_date: string | null
  purchase_price: number | null
  purchase_store: string | null
  warranty_end_date: string | null
  warranty_type: string | null
  energy_rating: string | null
  photo_url: string | null
  manual_document_id: number | null
  receipt_document_id: number | null
  service_contact_id: number | null
  is_active: boolean
  disposed_at: string | null
  created_at: string
  updated_at: string
}

export interface HomeAssetCreate {
  group_id: number
  name: string
  asset_type: string
  location_id?: number | null
  brand?: string | null
  model_number?: string | null
  serial_number?: string | null
  purchase_date?: string | null
  purchase_price?: number | null
  purchase_store?: string | null
  warranty_end_date?: string | null
  warranty_type?: string | null
  energy_rating?: string | null
  photo_url?: string | null
  manual_document_id?: number | null
  receipt_document_id?: number | null
  service_contact_id?: number | null
}

export interface HomeAssetUpdate {
  name?: string | null
  asset_type?: string | null
  location_id?: number | null
  brand?: string | null
  model_number?: string | null
  serial_number?: string | null
  purchase_date?: string | null
  purchase_price?: number | null
  purchase_store?: string | null
  warranty_end_date?: string | null
  warranty_type?: string | null
  energy_rating?: string | null
  photo_url?: string | null
  manual_document_id?: number | null
  receipt_document_id?: number | null
  service_contact_id?: number | null
  is_active?: boolean | null
}

export interface HomeAssetDisposeRequest {
  disposed_at: string
}

export interface MaintenanceTaskResponse {
  id: number
  asset_id: number
  name: string
  frequency_days: number | null
  priority: string | null
  instructions: string | null
  estimated_duration_minutes: number | null
  estimated_cost: number | null
  required_item_concept_id: number | null
  last_completed_at: string | null
  next_due_date: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface MaintenanceTaskCreate {
  asset_id: number
  name: string
  frequency_days?: number | null
  priority?: string | null
  instructions?: string | null
  estimated_duration_minutes?: number | null
  estimated_cost?: number | null
  required_item_concept_id?: number | null
}

export interface MaintenanceTaskUpdate {
  name?: string | null
  frequency_days?: number | null
  priority?: string | null
  instructions?: string | null
  estimated_duration_minutes?: number | null
  estimated_cost?: number | null
  required_item_concept_id?: number | null
  is_active?: boolean | null
}

export interface MaintenanceLogResponse {
  id: number
  task_id: number
  user_id: number
  completed_at: string
  actual_duration_minutes: number | null
  notes: string | null
  photo_url: string | null
  quality_rating: number | null
  cost_expense_id: number | null
  created_at: string
  updated_at: string
}

export interface MaintenanceCompleteRequest {
  actual_duration_minutes?: number | null
  notes?: string | null
  photo_url?: string | null
  quality_rating?: number | null
  cost_expense_id?: number | null
}

export interface AssetInsuranceResponse {
  id: number
  group_id: number
  policy_number: string
  provider_name: string
  coverage_type: string
  premium_amount: number
  premium_frequency: string
  start_date: string
  end_date: string | null
  deductible_amount: number | null
  document_id: number | null
  created_at: string
  updated_at: string
}

export interface AssetInsuranceCreate {
  group_id: number
  policy_number: string
  provider_name: string
  coverage_type: string
  premium_amount: number
  premium_frequency: string
  start_date: string
  end_date?: string | null
  deductible_amount?: number | null
  document_id?: number | null
}

export interface AssetInsuranceUpdate {
  policy_number?: string | null
  provider_name?: string | null
  coverage_type?: string | null
  premium_amount?: number | null
  premium_frequency?: string | null
  end_date?: string | null
  deductible_amount?: number | null
  document_id?: number | null
}
