/**
 * 认证相关类型定义
 */

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// Token 响应
export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  user_info: UserInfo
}

// 用户信息
export interface UserInfo {
  id: number
  username: string
  email?: string
  full_name?: string
  is_active?: boolean
  is_superuser?: boolean
  roles: string[]
  permissions: string[]
}

// 角色信息
export interface RoleInfo {
  id: number
  code: string
  name: string
}
