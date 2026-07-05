/**
 * 路由配置
 */
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import type { App } from 'vue'
import { setupRouterGuard } from './guard'
import { DYNAMIC_ROUTE_CONFIGS } from '@/config/permission-routes'

// Layout 布局组件
export const Layout = () => import('@/layout/index.vue')

const dynamicRoutes = DYNAMIC_ROUTE_CONFIGS as unknown as RouteRecordRaw[]

// 静态路由（无需权限）
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: {
      title: '登录',
      hidden: true
    }
  },
  {
    // 根布局路由：预注册业务路由，避免直达动态页面时先出现无匹配告警。
    path: '/',
    name: 'Layout',
    component: Layout,
    redirect: '/dashboard',
    meta: {
      hidden: true
    },
    children: dynamicRoutes
  },
  {
    path: '/403',
    name: '403',
    component: () => import('@/views/error/403.vue'),
    meta: {
      title: '无权限',
      hidden: true
    }
  },
  {
    path: '/404',
    name: '404',
    component: () => import('@/views/error/404.vue'),
    meta: {
      title: '页面不存在',
      hidden: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFoundCatchAll',
    redirect: '/404',
    meta: {
      hidden: true
    }
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: constantRoutes,
  scrollBehavior: () => ({ top: 0 })
})

// 配置路由
export function setupRouter(app: App<Element>) {
  app.use(router)
  // 创建路由守卫
  setupRouterGuard(router)
}

export default router
