/**
 * Dashboard 仪表盘相关接口
 */
import request from '@/utils/request'
import type { ApiResponse, DashboardQuery, DashboardOverview } from '@/types'

/**
 * 获取仪表盘全量数据
 */
export function getDashboardOverview(
  params: DashboardQuery
): Promise<ApiResponse<DashboardOverview>> {
  return request.get('/dashboard/overview', { params })
}
