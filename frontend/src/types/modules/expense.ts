/**
 * 费用相关类型定义
 */
import type { PageParams } from './common'

export interface ExpenseTypeInfo {
  id: number
  name: string
  code: string
  category: string
  description?: string
}

export interface ExpenseRecordInfo {
  id: number
  store_id: number
  store_name: string
  expense_type_id: number
  expense_type_name: string
  expense_type_code: string
  amount: number
  expense_date: string
  remark?: string
  created_at: string
}

export interface ExpenseRecordQuery extends PageParams {
  store_id?: number
  expense_type_id?: number
  start_date?: string
  end_date?: string
}
