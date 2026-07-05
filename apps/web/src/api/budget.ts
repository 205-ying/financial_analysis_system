import request from '@/utils/request'
import type { ApiResponse } from '@/types/modules/common'
import type { BudgetBatchCreate, BudgetAnalysisResponse, BudgetQuery } from '@/types/modules/budget'

/**
 * 批量保存预算
 */
export function batchSaveBudgets(data: BudgetBatchCreate): Promise<ApiResponse<void>> {
  return request.post('/budgets/batch', data)
}

/**
 * 获取预算分析报表
 */
export function getBudgetAnalysis(params: BudgetQuery): Promise<ApiResponse<BudgetAnalysisResponse>> {
  return request.get('/budgets/analysis', { params })
}
