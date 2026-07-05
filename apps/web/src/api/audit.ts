/**
 * 审计日志 API
 */

import request from '@/utils/request'
import type { ApiResponse } from '@/types'

/**
 * 审计日志列表查询参数
 */
export interface AuditLogQuery {
  page?: number
  page_size?: number
  user_id?: number
  username?: string
  action?: string
  resource_type?: string
  status?: string
  start_date?: string
  end_date?: string
  sort_by?: string
  sort_order?: string
}

/**
 * 审计日志数据
 */
export interface AuditLog {
  id: number
  user_id: number | null
  username: string
  action: string
  resource_type: string | null
  resource_id: number | null
  detail: string | null
  ip_address: string | null
  user_agent: string | null
  status: string
  error_message: string | null
  created_at: string
  updated_at: string
}

/**
 * 审计日志列表响应
 */
export interface AuditLogListResponse {
  total: number
  page: number
  page_size: number
  total_pages: number
  items: AuditLog[]
}

/**
 * 获取审计日志列表
 */
export function getAuditLogs(params: AuditLogQuery): Promise<ApiResponse<AuditLogListResponse>> {
  return request.get('/audit/logs', { params })
}

/**
 * 获取审计日志详情
 */
export function getAuditLogDetail(id: number): Promise<ApiResponse<AuditLog>> {
  return request.get(`/audit/logs/${id}`)
}

/**
 * 获取所有操作类型
 */
export function getAuditActions(): Promise<ApiResponse<string[]>> {
  return request.get('/audit/actions')
}

/**
 * 获取所有资源类型
 */
export function getResourceTypes(): Promise<ApiResponse<string[]>> {
  return request.get('/audit/resource-types')
}
