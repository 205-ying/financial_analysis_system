/**
 * 数据导入相关类型定义
 */

// 导入来源类型（对应后端 ImportSourceType）
export enum ImportSourceType {
  EXCEL = 'excel',
  CSV = 'csv'
}

// 导入目标类型（对应后端 ImportTargetType）
export enum ImportTargetType {
  ORDERS = 'orders',
  EXPENSE_RECORDS = 'expense_records',
  STORES = 'stores',
  EXPENSE_TYPES = 'expense_types'
}

// 导入任务状态（对应后端 ImportJobStatus）
export enum ImportJobStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  SUCCESS = 'success',
  PARTIAL_FAIL = 'partial_fail',
  FAIL = 'fail'
}

// 导入任务
export interface ImportJob {
  id: number
  filename: string
  source_type: ImportSourceType
  target_type: ImportTargetType
  status: ImportJobStatus
  store_id?: number
  store_name?: string
  total_rows: number
  success_rows: number
  fail_rows: number
  created_by_id: number
  created_by_name?: string
  created_at: string
  started_at?: string
  finished_at?: string
}

// 导入任务详情（包含用户信息）
export interface ImportJobDetail extends ImportJob {
  file_path: string
  error_report_path?: string
  config?: Record<string, unknown>
  created_by?: {
    id: number
    username: string
    real_name?: string
  }
}

// 导入错误记录
export interface ImportJobError {
  id: number
  job_id: number
  row_number: number
  error_type: string
  error_message: string
  raw_data?: Record<string, unknown>
  created_at: string
}

// 创建导入任务请求
export interface ImportJobCreateRequest {
  file: File
  target_type: ImportTargetType
  store_id?: number
}

// 导入任务查询参数
export interface ImportJobQuery {
  page: number
  page_size: number
  target_type?: ImportTargetType
  status?: ImportJobStatus
  start_date?: string
  end_date?: string
  keyword?: string
}

// 导入错误查询参数
export interface ImportJobErrorQuery {
  page: number
  page_size: number
}

// 状态显示映射
export const ImportJobStatusMap = {
  [ImportJobStatus.PENDING]: { text: '待处理', color: 'info', type: 'info' as const },
  [ImportJobStatus.RUNNING]: { text: '运行中', color: 'warning', type: 'warning' as const },
  [ImportJobStatus.SUCCESS]: { text: '全部成功', color: 'success', type: 'success' as const },
  [ImportJobStatus.PARTIAL_FAIL]: { text: '部分失败', color: 'warning', type: 'warning' as const },
  [ImportJobStatus.FAIL]: { text: '全部失败', color: 'danger', type: 'danger' as const }
}

// 目标类型显示映射
export const ImportTargetTypeMap = {
  [ImportTargetType.ORDERS]: '订单数据',
  [ImportTargetType.EXPENSE_RECORDS]: '费用记录',
  [ImportTargetType.STORES]: '门店信息',
  [ImportTargetType.EXPENSE_TYPES]: '费用科目'
}

// 创建任务时可选的导入类型（仅包含后端已实现）
export const ImportTargetTypeCreateMap = {
  [ImportTargetType.ORDERS]: '订单数据',
  [ImportTargetType.EXPENSE_RECORDS]: '费用记录'
}

// 来源类型显示映射
export const ImportSourceTypeMap = {
  [ImportSourceType.EXCEL]: 'Excel',
  [ImportSourceType.CSV]: 'CSV'
}
