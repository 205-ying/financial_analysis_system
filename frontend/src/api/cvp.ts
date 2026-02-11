import request from '@/utils/request'
import type { ApiResponse } from '@/types/modules/common'
import type { CVPAnalysisResult, CostBehaviorUpdate, CVPSimulation, CVPSimulationResult, CVPQuery } from '@/types/modules/cvp'

/**
 * 设置成本习性
 */
export function updateCostBehavior(data: CostBehaviorUpdate): Promise<ApiResponse<void>> {
  return request.put('/cvp/config', data)
}

/**
 * 获取本量利分析
 */
export function getCVPAnalysis(params: CVPQuery): Promise<ApiResponse<CVPAnalysisResult>> {
  return request.get('/cvp/analysis', { params })
}

/**
 * CVP 敏感性分析模拟
 */
export function simulateCVP(params: CVPQuery, data: CVPSimulation): Promise<ApiResponse<CVPSimulationResult>> {
  return request.post('/cvp/simulate', data, { params })
}
