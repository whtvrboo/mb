/** Finance module types: Expense, Settlement, Budget, Category, RecurringExpense, SplitPreset */

export interface ExpenseResponse {
  id: number
  group_id: number
  paid_by_user_id: number
  description: string
  amount: number
  currency_code: string
  category_id: number | null
  expense_date: string
  payment_method: string | null
  vendor_name: string | null
  receipt_img_url: string | null
  is_reimbursable: boolean
  exchange_rate: number | null
  is_recurring_generated: boolean
  linked_proposal_id: number | null
  linked_pet_medical_id: number | null
  linked_maintenance_log_id: number | null
  linked_recurring_expense_id: number | null
  version_id: number
  created_at: string
  updated_at: string
  splits?: ExpenseSplitResponse[]
}

export interface ExpenseSplitResponse {
  id: number
  expense_id: number
  user_id: number
  owed_amount: number
  is_paid: boolean
  paid_at: string | null
  manual_override: boolean
  created_at: string
  updated_at: string
}

export interface ExpenseCreateRequest {
  description: string
  amount: number
  currency_code: string
  category_id?: number | null
  expense_date: string
  payment_method?: string | null
  vendor_name?: string | null
  receipt_img_url?: string | null
  is_reimbursable?: boolean
  exchange_rate?: number | null
  splits?: { user_id: number; owed_amount: number; manual_override?: boolean }[]
  linked_proposal_id?: number | null
  linked_pet_medical_id?: number | null
  linked_maintenance_log_id?: number | null
}

export interface ExpenseUpdate {
  version_id: number
  description?: string | null
  amount?: number | null
  currency_code?: string | null
  category_id?: number | null
  expense_date?: string | null
  payment_method?: string | null
  vendor_name?: string | null
  receipt_img_url?: string | null
  is_reimbursable?: boolean
  exchange_rate?: number | null
}

export interface CategoryResponse {
  id: number
  group_id: number | null
  name: string
  icon_emoji: string | null
  color_hex: string | null
  parent_category_id: number | null
  is_income: boolean
  created_at: string
  updated_at: string
}

export interface CategoryCreate {
  name: string
  group_id?: number | null
  icon_emoji?: string | null
  color_hex?: string | null
  parent_category_id?: number | null
  is_income?: boolean
}

export interface CategoryUpdate {
  name?: string | null
  icon_emoji?: string | null
  color_hex?: string | null
  parent_category_id?: number | null
  is_income?: boolean
}

export interface UserBalanceResponse {
  user_id: number
  balance: number
  currency_code: string
}

export interface GroupBalanceSummaryResponse {
  group_id: number
  balances: UserBalanceResponse[]
  total_owed: number
  currency_code: string
}

export interface BalanceSnapshotResponse {
  id: number
  group_id: number
  user_id: number
  balance_amount: number
  currency_code: string
  snapshot_date: string
  created_at: string
  updated_at: string
}

export interface SettlementResponse {
  id: number
  group_id: number
  payer_id: number
  payee_id: number
  amount: number
  currency_code: string
  method: string | null
  settled_at: string
  confirmation_code: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface SettlementCreateRequest {
  payee_id: number
  amount: number
  currency_code: string
  method?: string | null
  settled_at?: string | null
  confirmation_code?: string | null
  notes?: string | null
}

export interface BudgetResponse {
  id: number
  group_id: number
  category_id: number
  amount_limit: number
  currency_code: string
  period_type: string
  start_date: string
  end_date: string | null
  alert_threshold_percentage: number | null
  created_at: string
  updated_at: string
}

export interface BudgetStatusResponse extends BudgetResponse {
  current_spent?: number
  remaining?: number
  percentage_used?: number
  is_over_budget?: boolean
  is_alert_threshold_reached?: boolean
}

export interface BudgetCreateRequest {
  category_id: number
  amount_limit: number
  currency_code: string
  period_type: string
  start_date: string
  end_date?: string | null
  alert_threshold_percentage?: number | null
}

export interface BudgetUpdate {
  amount_limit?: number | null
  end_date?: string | null
  alert_threshold_percentage?: number | null
}

export interface RecurringExpenseResponse {
  id: number
  group_id: number
  paid_by_user_id: number
  description: string
  amount: number
  currency_code: string
  category_id: number | null
  frequency_type: string
  interval_value: number
  start_date: string
  end_date: string | null
  auto_create_expense: boolean
  next_due_date: string | null
  split_preset_id: number | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface RecurringExpenseCreateRequest {
  description: string
  amount: number
  currency_code: string
  category_id?: number | null
  frequency_type: string
  interval_value?: number
  start_date: string
  end_date?: string | null
  auto_create_expense?: boolean
  split_preset_id?: number | null
}

export interface RecurringExpenseUpdate {
  description?: string | null
  amount?: number | null
  currency_code?: string | null
  category_id?: number | null
  frequency_type?: string | null
  interval_value?: number | null
  end_date?: string | null
  auto_create_expense?: boolean | null
  split_preset_id?: number | null
  is_active?: boolean | null
}

export interface SplitPresetMemberResponse {
  id: number
  preset_id: number
  user_id: number
  percentage: number | null
  fixed_amount: number | null
  created_at: string
  updated_at: string
}

export interface SplitPresetResponse {
  id: number
  group_id: number
  name: string
  is_default: boolean
  method: string
  created_at: string
  updated_at: string
  members?: SplitPresetMemberResponse[]
}

export interface SplitPresetCreateRequest {
  name: string
  method: string
  is_default?: boolean
  members?: { user_id: number; percentage?: number | null; fixed_amount?: number | null }[]
}

export interface SplitPresetUpdate {
  name?: string | null
  method?: string | null
  is_default?: boolean | null
  members?: { user_id: number; percentage?: number | null; fixed_amount?: number | null }[] | null
}
