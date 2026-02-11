/**
 * 路由守卫
 */
import type { Router } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

// 白名单（无需登录即可访问）
const whiteList = ['/login', '/403', '/404']

/**
 * 设置路由守卫
 */
export function setupRouterGuard(router: Router) {
  // 标记是否正在处理认证错误，避免重复提示
  let isHandlingAuthError = false

  // 全局前置守卫
  router.beforeEach(async (to, from, next) => {
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
          // 已生成路由，直接放行
          next()
        } else {
          try {
            // 获取用户信息和权限
            await authStore.getUserInfo()

            // 根据权限生成动态路由
            const accessRoutes = permissionStore.generateRoutes()

            // 动态添加路由
            const layoutRoute = {
              path: '/',
              component: () => import('@/layout/index.vue'),
              children: accessRoutes
            }
            router.addRoute(layoutRoute)

            // 添加 404 路由（必须在最后）
            router.addRoute({
              path: '/:pathMatch(.*)*',
              redirect: '/404',
              meta: { hidden: true }
            })

            // 重新导航到目标路由
            next({ ...to, replace: true })
          } catch (error) {
            console.error('获取用户信息失败：', error)
            
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
  router.afterEach((to) => {
    // 可以在这里添加页面访问统计等逻辑
  })

  // 全局错误处理
  router.onError((error) => {
    console.error('路由错误：', error)
    ElMessage.error('页面加载失败')
  })
}
