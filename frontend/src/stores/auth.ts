/**
 * 认证状态管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getCurrentUser, logout as logoutApi } from '@/api/auth'
import type { LoginRequest, UserInfo } from '@/types'
import router from '@/router'
import { STORAGE_KEYS } from '@/config'

export const useAuthStore = defineStore(
  'auth',
  () => {
    // State
    const token = ref<string>('')
    const userInfo = ref<UserInfo | null>(null)
    const permissions = ref<string[]>([])
    const accessibleStores = ref<number[] | null>(null) // null=全部门店, []=无权限, [id1,id2]=限定门店

    // Getters
    const isLoggedIn = computed(() => !!token.value)
    const username = computed(() => userInfo.value?.username || '')
    const roles = computed(() => userInfo.value?.roles || [])
    
    /**
     * 是否可以访问所有门店
     * - 超级管理员：true
     * - accessibleStores为null：true（无限制）
     * - 其他：false
     */
    const canAccessAllStores = computed(() => {
      return userInfo.value?.is_superuser || accessibleStores.value === null
    })

    // Actions
    /**
     * 登录
     */
    async function login(loginData: LoginRequest) {
      try {
        const response = await loginApi(loginData)
        const data = response.data

        // 保存 token 和用户信息
        token.value = data.access_token
        userInfo.value = data.user_info
        permissions.value = data.user_info.permissions

        return data
      } catch (error) {
        console.error('登录失败：', error)
        throw error
      }
    }

    /**
     * 获取用户信息
     */
    async function getUserInfo() {
      try {
        const response = await getCurrentUser()
        userInfo.value = response.data
        permissions.value = response.data.permissions
        
        // 缓存可访问门店列表
        // accessible_stores: null=全部, []=无权限, [id1,id2]=限定门店
        accessibleStores.value = (response.data as any).accessible_stores ?? null
        
        return response.data
      } catch (error) {
        console.error('获取用户信息失败：', error)
        throw error
      }
    }

    /**
     * 登出
     * @param silent 静默登出（不跳转登录页，不调用后端接口）
     */
    async function logout(silent = false) {
      try {
        if (!silent) {
          // 调用后端登出接口（可选）
          await logoutApi().catch(() => {
            // 忽略登出接口错误
          })
        }
      } finally {
        // 清除本地数据
        token.value = ''
        userInfo.value = null
        permissions.value = []
        accessibleStores.value = null

        // 跳转到登录页（静默模式下不跳转）
        if (!silent) {
          router.push('/login')
        }
      }
    }

    /**
     * 检查权限
     */
    function hasPermission(permission: string): boolean {
      if (!permissions.value || permissions.value.length === 0) {
        return false
      }

      // 超级管理员拥有所有权限
      if (permissions.value.includes('*:*:*')) {
        return true
      }

      return permissions.value.includes(permission)
    }

    /**
     * 检查多个权限（需要全部满足）
     */
    function hasPermissions(requiredPermissions: string[]): boolean {
      return requiredPermissions.every(p => hasPermission(p))
    }

    /**
     * 检查是否有任一权限
     */
    function hasAnyPermission(requiredPermissions: string[]): boolean {
      return requiredPermissions.some(p => hasPermission(p))
    }

    return {
      // State
      token,
      userInfo,
      permissions,
      accessibleStores,
      // Getters
      isLoggedIn,
      username,
      roles,
      canAccessAllStores,
      // Actions
      login,
      getUserInfo,
      logout,
      hasPermission,
      hasPermissions,
      hasAnyPermission
    }
  },
  {
    // 持久化到 localStorage
    persist: {
      key: STORAGE_KEYS.AUTH,
      storage: localStorage,
      paths: ['token', 'userInfo', 'permissions', 'accessibleStores']
    }
  }
)
