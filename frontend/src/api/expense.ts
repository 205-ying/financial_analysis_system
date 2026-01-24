/**
 * 费用相关接口
 */
import request from '@/utils/request'
import type {
  ApiResponse,
  ExpenseTypeInfo,
  ExpenseRecordInfo,
  ExpenseRecordQuery,
  PageData
} from '@/types'

/**
 * 获取费用类型列表
 */
export function getExpenseTypeList(): Promise<ApiResponse<ExpenseTypeInfo[]>> {
  return request.get('/expense-types/all')
}

/**
 * 获取费用记录列表
 */
export function getExpenseRecordList(
  params: ExpenseRecordQuery
): Promise<ApiResponse<PageData<ExpenseRecordInfo>>> {
  return request.get('/expense-records', { params })
}

/**
 * 获取费用记录详情
 */
export function getExpenseRecordDetail(id: number): Promise<ApiResponse<ExpenseRecordInfo>> {
  return request.get(`/expense-records/${id}`)
}
