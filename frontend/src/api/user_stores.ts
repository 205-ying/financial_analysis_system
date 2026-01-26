/**
 * 用户门店权限管理 API
 */
import request from '@/utils/request'

/**
 * 用户门店权限信息
 */
export interface UserStorePermission {
  store_id: number
  store_name: string
  assigned_at: string
}

/**
 * 用户门店列表响应
 */
export interface UserStoresResponse {
  user_id: number
  username: string
  stores: UserStorePermission[]
  total: number
}

/**
 * 分配门店权限请求
 */
export interface AssignUserStoresRequest {
  user_id: number
  store_ids: number[]
}

/**
 * 获取用户的门店权限列表
 */
export function getUserStores(userId: number) {
  return request.get<UserStoresResponse>(`/user-stores`, {
    params: { user_id: userId }
  })
}

/**
 * 分配门店权限（覆盖式更新）
 */
export function assignUserStores(data: AssignUserStoresRequest) {
  return request.post('/user-stores/assign', data)
}

/**
 * 删除用户的所有门店权限
 */
export function deleteUserStores(userId: number) {
  return request.delete(`/user-stores`, {
    params: { user_id: userId }
  })
}
