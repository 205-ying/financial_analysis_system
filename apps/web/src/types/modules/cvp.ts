export interface CVPAnalysisResult {
  total_revenue: number
  variable_cost: number
  fixed_cost: number
  contribution_margin: number
  contribution_margin_rate: number
  break_even_point: number
  break_even_sales_ratio: number
  safety_margin: number
  safety_margin_rate: number
  operating_leverage: number
  operating_profit: number
}

export interface CostBehaviorUpdate {
  expense_type_id: number
  cost_behavior: 'fixed' | 'variable'
}

export interface CVPSimulation {
  fixed_cost_change_rate: number
  variable_cost_change_rate: number
}

export interface CVPSimulationResult {
  original_bep: number
  simulated_bep: number
  bep_change: number
  bep_change_rate: number
}

export interface CVPQuery {
  start_date: string
  end_date: string
  store_id?: number
}
