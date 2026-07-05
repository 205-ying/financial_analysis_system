/**
 * 同比环比时间对比分析相关类型定义
 */

/** 对比分析查询参数 */
export interface ComparisonQuery {
  start_date: string
  end_date: string
  compare_type?: 'yoy' | 'mom' | 'custom'
  compare_start_date?: string
  compare_end_date?: string
  store_id?: number
}

/** 趋势对比查询参数（含指标） */
export interface TrendComparisonQuery extends ComparisonQuery {
  metric?: string
}

/** 单指标对比结果 */
export interface MetricComparison {
  metric_name: string
  metric_label: string
  current_value: number
  previous_value: number
  difference: number
  growth_rate: number | null
}

/** 期间对比汇总响应 */
export interface PeriodComparisonResponse {
  current_period: string
  previous_period: string
  metrics: MetricComparison[]
}

/** 趋势对比数据项 */
export interface TrendComparisonItem {
  date_label: string
  current_value: number
  previous_value: number
}

/** 趋势对比响应 */
export interface TrendComparisonResponse {
  current_period: string
  previous_period: string
  metric_name: string
  metric_label: string
  data: TrendComparisonItem[]
}

/** 门店对比数据项 */
export interface StoreComparisonItem {
  store_id: number
  store_name: string
  current_revenue: number
  previous_revenue: number
  revenue_growth_rate: number | null
  current_profit: number
  previous_profit: number
  profit_growth_rate: number | null
  current_order_count: number
  previous_order_count: number
  order_growth_rate: number | null
  current_avg_order_value: number
  previous_avg_order_value: number
  avg_order_value_growth_rate: number | null
}
