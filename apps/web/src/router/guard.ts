/**
 * 路由守卫
 */
import type { RouteLocationNormalized, Router } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

// 白名单（无需登录即可访问）
const whiteList = ['/login', '/403', '/404']

function canAccessRoute(to: RouteLocationNormalized, authStore: ReturnType<typeof useAuthStore>) {
  return to.matched.every((record) => {
    const permissions = record.meta?.permissions
    if (!Array.isArray(permissions) || permissions.length === 0) return true

    return authStore.hasAnyPermission([...permissions])
  })
}

/**
 * 设置路由守卫
 */
export function setupRouterGuard(router: Router) {
  // 标记是否正在处理认证错误，避免重复提示
  let isHandlingAuthError = false

  // 全局前置守卫
  router.beforeEach(async (to, _from, next) => {
    const authStore = useAuthStore()
    const permissionStore = usePermissionStore()

    // 设置页面标题
    document.title = `${to.meta.title || '财务分析系统'} - 财务分析系统`

    // 检查是否已登录
    if (authStore.isLoggedIn) {
      if (to.path === '/login') {
        // 已登录，跳转到首页
        next({ path: '/' })
      } else {
        // 检查是否已生成动态路由
        const hasRoutes = permissionStore.routes && permissionStore.routes.length > 0

        if (hasRoutes) {
          if (!canAccessRoute(to, authStore)) {
            next('/403')
            return
          }

          // 已生成路由，直接放行
          next()
        } else {
          try {
            // 获取用户信息和权限（登录接口已返回 user_info 时可跳过一次 /me）
            if (!authStore.userInfo || !authStore.permissions || authStore.permissions.length === 0) {
              await authStore.getUserInfo()
            }

            // 根据权限生成动态路由
            const accessRoutes = permissionStore.generateRoutes()

            // 兼容未来按需路由：当前业务路由已预注册，缺失时再补充注入。
            accessRoutes.forEach((child) => {
              if (!child.name || !router.hasRoute(child.name)) {
                router.addRoute('Layout', child)
              }
            })

            if (!canAccessRoute(to, authStore)) {
              next('/403')
              return
            }

            // 重新导航到目标路由
            next({ ...to, replace: true })
          } catch (error) {
            // 避免重复显示错误提示
            if (!isHandlingAuthError) {
              isHandlingAuthError = true
              
              // 清除 token 并跳转登录
              authStore.logout()
              ElMessage.error('获取用户信息失败，请重新登录')
              
              // 延迟重置标记
              setTimeout(() => {
                isHandlingAuthError = false
              }, 1000)
            }
            
            next(`/login?redirect=${to.path}`)
          }
        }
      }
    } else {
      // 未登录
      if (whiteList.includes(to.path)) {
        // 在白名单中，直接放行
        next()
      } else {
        // 不在白名单中，跳转登录页
        next(`/login?redirect=${to.path}`)
      }
    }
  })

  // 全局后置守卫
  router.afterEach(() => {
    // 可以在这里添加页面访问统计等逻辑
  })

  // 全局错误处理
  router.onError((_error) => {
    ElMessage.error('页面加载失败')
  })
}
