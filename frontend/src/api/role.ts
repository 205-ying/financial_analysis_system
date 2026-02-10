/**
 * 角色管理 API
 */

import request from '@/utils/request'
import type { PaginatedResponse, Response } from '@/types/common'

// 角色类型定义
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

export interface Role {
  id: number
  code: string
  name: string
  description?: string
  is_active: boolean
  permissions: Permission[]
  created_at: string
  updated_at: string
}

export interface RoleListItem {
  id: number
  code: string
  name: string
  description?: string
  is_active: boolean
  permission_count: number
  user_count: number
  created_at: string
  updated_at: string
}

export interface RoleCreateParams {
  code: string
  name: string
  description?: string
  is_active?: boolean
  permission_ids?: number[]
}

export interface RoleUpdateParams {
  name?: string
  description?: string
  is_active?: boolean
}

export interface RoleListParams {
  page?: number
  page_size?: number
  search?: string
  is_active?: boolean
}

export interface AssignPermissionsParams {
  permission_ids: number[]
}

// API 方法
export const roleApi = {
  /**
   * 获取角色列表
   */
  getList: (params: RoleListParams) =>
    request.get<PaginatedResponse<RoleListItem[]>>('/roles', { params }),

  /**
   * 获取角色详情
   */
  getDetail: (id: number) =>
    request.get<Response<Role>>(`/roles/${id}`),

  /**
   * 创建角色
   */
  create: (data: RoleCreateParams) =>
    request.post<Response<Role>>('/roles', data),

  /**
   * 更新角色
   */
  update: (id: number, data: RoleUpdateParams) =>
    request.put<Response<Role>>(`/roles/${id}`, data),

  /**
   * 删除角色
   */
  delete: (id: number) =>
    request.delete<Response<null>>(`/roles/${id}`),

  /**
   * 分配权限
   */
  assignPermissions: (id: number, data: AssignPermissionsParams) =>
    request.post<Response<Role>>(`/roles/${id}/permissions`, data)
}
