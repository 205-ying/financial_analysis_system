export interface Budget {
  id: number
  store_id: number
  expense_type_id: number
  year: number
  month: number
  amount: number
  created_at?: string
  updated_at?: string
}

export interface BudgetItemInput {
  expense_type_id: number
  amount: number
}

export interface BudgetBatchCreate {
  store_id: number
  year: number
  month: number
  items: BudgetItemInput[]
}

export interface BudgetAnalysisItem {
  expense_type_id: number
  expense_type_name: string
  budget_amount: number
  actual_amount: number
  variance: number        // 差异额 = 实际 - 预算
  variance_rate: number   // 差异率 %
  is_over_budget: boolean // 是否超支
}

export interface BudgetAnalysisResponse {
  total_budget: number
  total_actual: number
  total_variance: number
  items: BudgetAnalysisItem[]
}

export interface BudgetQuery {
  store_id: number
  year: number
  month: number
}
