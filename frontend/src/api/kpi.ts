/**
 * KPI 分析相关接口
 */
import request from '@/utils/request'
import type {
  ApiResponse,
  KPIQuery,
  KPISummary,
  KPITrendItem,
  DailyKPI,
  ExpenseCategoryItem,
  StoreRankingItem
} from '@/types'

/**
 * 获取 KPI 汇总数据
 */
export function getKPISummary(params?: KPIQuery): Promise<ApiResponse<KPISummary>> {
  return request.get('/kpi/summary', { params })
}

/**
 * 获取 KPI 趋势数据
 */
export function getKPITrend(params?: KPIQuery): Promise<ApiResponse<KPITrendItem[]>> {
  return request.get('/kpi/trend', { params })
}

/**
 * 获取每日 KPI 明细
 */
export function getDailyKPI(params?: KPIQuery): Promise<ApiResponse<DailyKPI[]>> {
  return request.get('/kpi/daily', { params })
}

/**
 * 获取费用分类统计
 */
export function getExpenseCategory(params?: KPIQuery): Promise<ApiResponse<ExpenseCategoryItem[]>> {
  return request.get('/kpi/expense-category', { params })
}

/**
 * 获取门店排名
 */
export function getStoreRanking(params?: KPIQuery): Promise<ApiResponse<StoreRankingItem[]>> {
  return request.get('/kpi/store-ranking', { params })
}

/**
 * 重建 KPI 数据
 */
export function rebuildKPI(params?: {
  start_date?: string
  end_date?: string
}): Promise<ApiResponse<{ message: string; rows_affected: number }>> {
  return request.post('/api/v1/kpi/rebuild', params)
}
