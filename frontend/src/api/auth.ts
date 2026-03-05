/**
 * 认证相关 API
 */
import request from '@/utils/request'
import type { LoginRequest, TokenResponse, UserInfo, ApiResponse } from '@/types'

/**
 * 登录
 */
export function login(data: LoginRequest): Promise<ApiResponse<TokenResponse>> {
  return request.post('/auth/login', data)
}

/**
 * 获取当前用户信息（含权限）
 */
export function getCurrentUser(): Promise<ApiResponse<UserInfo>> {
  return request.get('/auth/me')
}

/**
 * 登出
 */
export function logout(): Promise<ApiResponse<void>> {
  return request.post('/auth/logout')
}
