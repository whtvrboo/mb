/** Lists module types: List, Item, InventoryItem */

export interface ListResponse {
  id: number
  group_id: number
  created_by_id: number
  name: string
  type: string
  deadline: string | null
  store_name: string | null
  estimated_total: number | null
  is_archived: boolean
  archived_at: string | null
  version_id: number
  created_at: string
  updated_at: string
}

export interface ListCreate {
  group_id: number
  name: string
  type?: string
  deadline?: string | null
  store_name?: string | null
  estimated_total?: number | null
}

export interface ListUpdate {
  name?: string | null
  deadline?: string | null
  is_archived?: boolean | null
}

export interface ItemResponse {
  id: number
  list_id: number
  added_by_id: number | null
  assigned_to_id: number | null
  name: string
  quantity_value: number
  quantity_unit: string | null
  is_checked: boolean
  checked_at: string | null
  price_estimate: number | null
  priority: number | null
  notes: string | null
  version_id: number
  created_at: string
  updated_at: string
}

export interface ItemCreate {
  list_id: number
  name: string
  quantity_value?: number
  quantity_unit?: string | null
  is_checked?: boolean
  price_estimate?: number | null
  priority?: number | null
  notes?: string | null
}

export interface ItemUpdate {
  name?: string | null
  quantity_value?: number | null
  quantity_unit?: string | null
  is_checked?: boolean | null
  price_estimate?: number | null
  priority?: number | null
  notes?: string | null
}

export interface ItemBulkCreate {
  items: ItemCreate[]
}

export interface ItemBulkResponse {
  items: ItemResponse[]
}

export interface InventoryItemResponse {
  id: number
  group_id: number
  location_id: number | null
  concept_id: number | null
  quantity_value: number
  quantity_unit: string | null
  expiration_date: string | null
  opened_date: string | null
  restock_threshold: number | null
  created_at: string
  updated_at: string
}

export interface InventoryItemUpdate {
  quantity_value?: number | null
  quantity_unit?: string | null
  expiration_date?: string | null
  opened_date?: string | null
  restock_threshold?: number | null
}
