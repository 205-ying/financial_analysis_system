/**
 * KPI 相关类型定义
 */

export interface KPIQuery {
  store_id?: number
  start_date?: string
  end_date?: string
  granularity?: 'day' | 'week' | 'month'
  top_n?: number
}

export interface DailyKPI {
  kpi_date: string
  store_id: number
  store_name: string
  total_revenue: number
  total_cost: number
  total_profit: number
  profit_rate: number
  order_count: number
  expense_count: number
}

export interface KPISummary {
  total_revenue: number
  total_cost: number
  total_profit: number
  profit_rate: number
  order_count: number
  expense_count: number
  store_count: number
  date_range: {
    start_date: string
    end_date: string
  }
}

export interface KPITrendItem {
  date: string
  revenue: number
  cost: number
  profit: number
  profit_rate: number
}

export interface ExpenseCategoryItem {
  category: string
  category_name: string
  amount: number
  percentage: number
}

export interface StoreRankingItem {
  store_id: number
  store_name: string
  total_revenue: number
  total_cost: number
  total_profit: number
  profit_rate: number
  rank: number
}
