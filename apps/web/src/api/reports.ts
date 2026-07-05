/**
 * 报表中心 API
 */
import request from '@/utils/request'
import type {
  ReportQuery,
  DailySummaryRow,
  MonthlySummaryRow,
  StorePerformanceRow,
  ExpenseBreakdownRow,
  ReportResponse
} from '@/types'

/**
 * 获取日汇总报表
 */
export const getDailySummary = (params: ReportQuery): Promise<ReportResponse<DailySummaryRow>> => {
  return request.get('/reports/daily-summary', { params })
}

/**
 * 获取月汇总报表
 */
export const getMonthlySummary = (params: ReportQuery): Promise<ReportResponse<MonthlySummaryRow>> => {
  return request.get('/reports/monthly-summary', { params })
}

/**
 * 获取门店绩效报表
 */
export const getStorePerformance = (params: ReportQuery): Promise<ReportResponse<StorePerformanceRow>> => {
  return request.get('/reports/store-performance', { params })
}

/**
 * 获取费用明细报表
 */
export const getExpenseBreakdown = (params: ReportQuery): Promise<ReportResponse<ExpenseBreakdownRow>> => {
  return request.get('/reports/expense-breakdown', { params })
}

/**
 * 导出报表Excel（返回Blob）
 */
export const exportReport = (params: ReportQuery): Promise<Blob> => {
  return request.get('/reports/export', {
    params,
    responseType: 'blob'
  })
}
