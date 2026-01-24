/**
 * 通用类型定义
 */

// 统一响应格式
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
}

// 分页参数
export interface PageParams {
  page: number
  page_size: number
}

// 分页响应
export interface PageData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// 查询参数基础接口
export interface BaseQuery extends PageParams {
  store_id?: number
  start_date?: string
  end_date?: string
}
