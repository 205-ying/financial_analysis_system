/**
 * 权限管理 API
 */

import request from '@/utils/request'
import type { PaginatedResponse, Response } from '@/types/common'

// 权限类型定义
export interface Permission {
  id: number
  code: string
  name: string
  resource: string
  action: string
  description?: string
  created_at: string
  updated_at: string
}

export interface PermissionListItem {
  id: number
  code: string
  name: string
  resource: string
  action: string
  description?: string
  role_count: number
  created_at: string
}

export interface PermissionListParams {
  page?: number
  page_size?: number
  search?: string
  resource?: string
}

// API 方法
export const permissionApi = {
  /**
   * 获取权限列表（分页）
   */
  getList: (params: PermissionListParams) =>
    request.get<PaginatedResponse<PermissionListItem[]>>('/permissions', { params }),

  /**
   * 获取所有权限（不分页，用于下拉选择）
   */
  getAll: () =>
    request.get<Response<Permission[]>>('/permissions/all'),

  /**
   * 获取所有资源类型
   */
  getResources: () =>
    request.get<Response<string[]>>('/permissions/resources'),

  /**
   * 获取权限详情
   */
  getDetail: (id: number) =>
    request.get<Response<Permission>>(`/permissions/${id}`)
}
