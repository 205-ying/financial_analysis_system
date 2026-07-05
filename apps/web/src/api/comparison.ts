/**
 * 同比环比时间对比分析相关接口
 */
import request from '@/utils/request'
import type {
  ApiResponse,
  ComparisonQuery,
  TrendComparisonQuery,
  PeriodComparisonResponse,
  TrendComparisonResponse,
  StoreComparisonItem
} from '@/types'

/**
 * 获取期间对比汇总
 */
export function getPeriodComparison(
  params: ComparisonQuery
): Promise<ApiResponse<PeriodComparisonResponse>> {
  return request.get('/comparison/period', { params })
}

/**
 * 获取趋势对比数据
 */
export function getTrendComparison(
  params: TrendComparisonQuery
): Promise<ApiResponse<TrendComparisonResponse>> {
  return request.get('/comparison/trend', { params })
}

/**
 * 获取门店对比分析
 */
export function getStoreComparison(
  params: ComparisonQuery
): Promise<ApiResponse<StoreComparisonItem[]>> {
  return request.get('/comparison/stores', { params })
}
