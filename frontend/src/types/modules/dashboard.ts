/**
 * Dashboard 仪表盘相关类型定义
 */

/** 核心指标卡片 */
export interface SummaryCard {
  label: string
  value: number
  unit: string
  yoy_growth: number | null
  mom_growth: number | null
}

/** 趋势数据点 */
export interface TrendDataPoint {
  date: string
  revenue: number
  cost: number
  profit: number
}

/** 门店排名项 */
export interface StoreRankItem {
  store_name: string
  revenue: number
  profit: number
}

/** 费用结构项 */
export interface ExpenseStructureItem {
  name: string
  value: number
}

/** 渠道收入分布 */
export interface ChannelDistribution {
  dine_in: number
  takeout: number
  delivery: number
  online: number
}

/** 仪表盘全量数据 */
export interface DashboardOverview {
  summary_cards: SummaryCard[]
  revenue_trend: TrendDataPoint[]
  store_ranking: StoreRankItem[]
  expense_structure: ExpenseStructureItem[]
  channel_distribution: ChannelDistribution
  profit_rate: number
  profit_rate_target: number
}

/** Dashboard 查询参数 */
export interface DashboardQuery {
  start_date: string
  end_date: string
  store_id?: number
}
