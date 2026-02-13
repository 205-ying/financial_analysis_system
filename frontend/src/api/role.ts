/**
 * 角色管理 API
 */

import request from '@/utils/request'
import type { PaginatedResponse, Response } from '@/types'

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

export interface RoleSimple {
  id: number
  code: string
  name: string
}

export interface UserRoleListItem {
  id: number
  username: string
  full_name?: string
  phone?: string
  email: string
  is_active: boolean
  roles: RoleSimple[]
  updated_at: string
}

export interface UserWithRoles {
  id: number
  username: string
  full_name?: string
  phone?: string
  email: string
  is_active: boolean
  roles: RoleSimple[]
}

export interface UserListParams {
  page?: number
  page_size?: number
  search?: string
  is_active?: boolean
}

export interface AssignUserRolesParams {
  role_ids: number[]
}

export interface UserCreateParams {
  username: string
  email: string
  password: string
  full_name?: string
  phone?: string
  is_active?: boolean
}

export interface UserUpdateParams {
  email?: string
  full_name?: string
  phone?: string
}

export interface UpdateUserStatusParams {
  is_active: boolean
}

// API 方法
export const roleApi = {
  /**
   * 获取角色列表
   */
  getList: (params: RoleListParams) => {
    const normalized: RoleListParams = {
      ...params,
      page_size: Math.min(params.page_size ?? 20, 100)
    }
    return request.get<PaginatedResponse<RoleListItem[]>>('/roles', { params: normalized })
  },

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
    request.post<Response<Role>>(`/roles/${id}/permissions`, data),

  /**
   * 获取用户列表（含角色）
   */
  getUserList: (params: UserListParams) =>
    request.get<PaginatedResponse<UserRoleListItem[]>>('/roles/users', { params }),

  /**
   * 获取用户角色详情
   */
  getUserRoles: (userId: number) =>
    request.get<Response<UserWithRoles>>(`/roles/users/${userId}/roles`),

  /**
   * 分配用户角色（覆盖式）
   */
  assignUserRoles: (userId: number, data: AssignUserRolesParams) =>
    request.put<Response<UserWithRoles>>(`/roles/users/${userId}/roles`, data),

  /**
   * 创建用户
   */
  createUser: (data: UserCreateParams) =>
    request.post<Response<UserWithRoles>>('/roles/users', data),

  /**
   * 更新用户基础信息
   */
  updateUser: (userId: number, data: UserUpdateParams) =>
    request.put<Response<UserWithRoles>>(`/roles/users/${userId}`, data),

  /**
   * 更新用户启用状态
   */
  updateUserStatus: (userId: number, data: UpdateUserStatusParams) =>
    request.put<Response<UserWithRoles>>(`/roles/users/${userId}/status`, data)
}
