/**
 * 财务运营中心接口
 */
import request from '@/utils/request'
import type {
  ApiResponse,
  FinanceCloseReadinessOverview,
  FinanceOperationsOverview,
  FinanceOperationsQuery,
  FinanceSuiteOverview,
} from '@/types'

export function getFinanceOperationsOverview(
  params: FinanceOperationsQuery
): Promise<ApiResponse<FinanceOperationsOverview>> {
  return request.get('/finance/operations-overview', { params })
}

export function getFinanceCloseReadiness(
  params: FinanceOperationsQuery
): Promise<ApiResponse<FinanceCloseReadinessOverview>> {
  return request.get('/finance/close-readiness', { params })
}

export function getFinanceSuiteOverview(
  params: FinanceOperationsQuery
): Promise<ApiResponse<FinanceSuiteOverview>> {
  return request.get('/finance/suite-overview', { params })
}
