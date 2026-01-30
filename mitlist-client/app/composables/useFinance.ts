import type {
  ExpenseResponse,
  ExpenseCreateRequest,
  ExpenseUpdate,
  GroupBalanceSummaryResponse,
  BalanceSnapshotResponse,
  CategoryResponse,
  CategoryCreate,
  CategoryUpdate,
  SettlementResponse,
  SettlementCreateRequest,
  BudgetResponse,
  BudgetStatusResponse,
  BudgetCreateRequest,
  BudgetUpdate,
  RecurringExpenseResponse,
  RecurringExpenseCreateRequest,
  RecurringExpenseUpdate,
  SplitPresetResponse,
  SplitPresetCreateRequest,
  SplitPresetUpdate,
} from '~/types/finance'

export function useFinance() {
  const $api = useNuxtApp().$api

  return {
    listExpenses: (params?: {
      user_id?: number
      category_id?: number
      date_from?: string
      date_to?: string
      limit?: number
      offset?: number
    }) => useApi<ExpenseResponse[]>('/expenses', { query: params }),
    getExpense: (expenseId: number) =>
      useApi<ExpenseResponse>(`/expenses/${expenseId}`),
    createExpense: (data: ExpenseCreateRequest) =>
      $api<ExpenseResponse>('/expenses', { method: 'POST', body: data }),
    updateExpense: (expenseId: number, data: ExpenseUpdate) =>
      $api<ExpenseResponse>(`/expenses/${expenseId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteExpense: (expenseId: number) =>
      $api<void>(`/expenses/${expenseId}`, { method: 'DELETE' }),

    getBalances: () =>
      useApi<GroupBalanceSummaryResponse>('/balances'),
    getBalanceHistory: (params?: { user_id?: number; limit?: number }) =>
      useApi<BalanceSnapshotResponse[]>('/balances/history', {
        query: params,
      }),

    listCategories: () => useApi<CategoryResponse[]>('/categories'),
    getCategory: (categoryId: number) =>
      useApi<CategoryResponse>(`/categories/${categoryId}`),
    createCategory: (data: CategoryCreate) =>
      $api<CategoryResponse>('/categories', { method: 'POST', body: data }),
    updateCategory: (categoryId: number, data: CategoryUpdate) =>
      $api<CategoryResponse>(`/categories/${categoryId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteCategory: (categoryId: number) =>
      $api<void>(`/categories/${categoryId}`, { method: 'DELETE' }),

    listSettlements: (params?: { limit?: number; offset?: number }) =>
      useApi<SettlementResponse[]>('/settlements', { query: params }),
    getSettlement: (settlementId: number) =>
      useApi<SettlementResponse>(`/settlements/${settlementId}`),
    createSettlement: (data: SettlementCreateRequest) =>
      $api<SettlementResponse>('/settlements', {
        method: 'POST',
        body: data,
      }),
    deleteSettlement: (settlementId: number) =>
      $api<void>(`/settlements/${settlementId}`, { method: 'DELETE' }),

    listBudgets: () => useApi<BudgetStatusResponse[]>('/budgets'),
    getBudget: (budgetId: number) =>
      useApi<BudgetStatusResponse>(`/budgets/${budgetId}`),
    createBudget: (data: BudgetCreateRequest) =>
      $api<BudgetResponse>('/budgets', { method: 'POST', body: data }),
    updateBudget: (budgetId: number, data: BudgetUpdate) =>
      $api<BudgetResponse>(`/budgets/${budgetId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteBudget: (budgetId: number) =>
      $api<void>(`/budgets/${budgetId}`, { method: 'DELETE' }),

    listRecurringExpenses: (params?: { active_only?: boolean }) =>
      useApi<RecurringExpenseResponse[]>('/recurring-expenses', {
        query: params,
      }),
    getRecurringExpense: (recurringId: number) =>
      useApi<RecurringExpenseResponse>(`/recurring-expenses/${recurringId}`),
    createRecurringExpense: (data: RecurringExpenseCreateRequest) =>
      $api<RecurringExpenseResponse>('/recurring-expenses', {
        method: 'POST',
        body: data,
      }),
    updateRecurringExpense: (
      recurringId: number,
      data: RecurringExpenseUpdate,
    ) =>
      $api<RecurringExpenseResponse>(`/recurring-expenses/${recurringId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteRecurringExpense: (recurringId: number) =>
      $api<void>(`/recurring-expenses/${recurringId}`, {
        method: 'DELETE',
      }),
    generateRecurringExpense: (recurringId: number) =>
      $api<ExpenseResponse>(
        `/recurring-expenses/${recurringId}/generate`,
        { method: 'POST' },
      ),

    listSplitPresets: () => useApi<SplitPresetResponse[]>('/split-presets'),
    getSplitPreset: (presetId: number) =>
      useApi<SplitPresetResponse>(`/split-presets/${presetId}`),
    createSplitPreset: (data: SplitPresetCreateRequest) =>
      $api<SplitPresetResponse>('/split-presets', {
        method: 'POST',
        body: data,
      }),
    updateSplitPreset: (presetId: number, data: SplitPresetUpdate) =>
      $api<SplitPresetResponse>(`/split-presets/${presetId}`, {
        method: 'PATCH',
        body: data,
      }),
    deleteSplitPreset: (presetId: number) =>
      $api<void>(`/split-presets/${presetId}`, { method: 'DELETE' }),
  }
}
