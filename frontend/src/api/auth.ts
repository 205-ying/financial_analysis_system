/**
 * 认证相关 API
 */
import request from '@/utils/request'
import type { LoginRequest, TokenResponse, UserInfo, ApiResponse } from '@/types'

/**
 * 登录
 */
export function login(data: LoginRequest) {
  return request<ApiResponse<TokenResponse>>({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 获取当前用户信息（含权限）
 */
export function getCurrentUser() {
  return request<ApiResponse<UserInfo>>({
    url: '/auth/me',
    method: 'get'
  })
}

/**
 * 登出
 */
export function logout() {
  return request<ApiResponse<void>>({
    url: '/auth/logout',
    method: 'post'
  })
}
