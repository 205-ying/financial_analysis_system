/**
 * 通用类型定义
 */

// 统一响应格式
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

export interface Response<T = unknown> extends ApiResponse<T> {}

export interface PaginatedResponse<T = unknown> {
  code: number
  message: string
  data: T
  total: number
  page: number
  page_size: number
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
