/**
 * 权限管理 Store
 */
import { defineStore } from 'pinia'
import { ref, markRaw } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from './auth'
import {
  DataAnalysis,
  Document,
  Money,
  TrendCharts,
  List,
  Upload
} from '@element-plus/icons-vue'

export const usePermissionStore = defineStore('permission', () => {
  // State
  const routes = ref<RouteRecordRaw[]>([])
  const dynamicRoutes = ref<RouteRecordRaw[]>([])

  // Actions
  /**
   * 根据权限生成可访问的路由
   */
  function generateRoutes(): RouteRecordRaw[] {
    const authStore = useAuthStore()
    const permissions = authStore.permissions

    // 定义所有动态路由
    const asyncRoutes: RouteRecordRaw[] = [
      {
        path: '/',
        redirect: '/dashboard'
      },
      {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: {
          title: '看板',
          icon: markRaw(DataAnalysis),
          requiresAuth: true,
          permissions: ['dashboard:view']
        }
      },
      {
        path: '/orders',
        name: 'Orders',
        component: () => import('@/views/orders/index.vue'),
        meta: {
          title: '订单管理',
          icon: markRaw(Document),
          requiresAuth: true,
          permissions: ['order:view']
        }
      },
      {
        path: '/expenses',
        name: 'Expenses',
        component: () => import('@/views/expenses/index.vue'),
        meta: {
          title: '费用管理',
          icon: markRaw(Money),
          requiresAuth: true,
          permissions: ['expense:view']
        }
      },
      {
        path: '/kpi',
        name: 'KPI',
        component: () => import('@/views/kpi/index.vue'),
        meta: {
          title: 'KPI 分析',
          icon: markRaw(TrendCharts),
          requiresAuth: true,
          permissions: ['kpi:view']
        }
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('@/views/analytics/ReportView.vue'),
        meta: {
          title: '报表中心',
          icon: markRaw(Document),
          requiresAuth: true,
          permissions: ['report:view']
        }
      },
      {
        path: '/audit-logs',
        name: 'AuditLogs',
        component: () => import('@/views/audit-logs/index.vue'),
        meta: {
          title: '审计日志',
          icon: markRaw(List),
          requiresAuth: true,
          permissions: ['audit:view']
        }
      },
      {
        path: '/system/import-jobs',
        name: 'ImportJobs',
        component: () => import('@/views/system/import/ImportJobListView.vue'),
        meta: {
          title: '数据导入',
          icon: markRaw(Upload),
          requiresAuth: true,
          permissions: ['import_job:view']
        }
      },
      {
        path: '/system/import-jobs/:id',
        name: 'ImportJobDetail',
        component: () => import('@/views/system/import/ImportJobDetailView.vue'),
        meta: {
          title: '导入详情',
          hidden: true,
          requiresAuth: true,
          permissions: ['import_job:view']
        }
      }
    ]

    // 过滤有权限访问的路由
    const accessedRoutes = filterAsyncRoutes(asyncRoutes, permissions)

    dynamicRoutes.value = accessedRoutes
    routes.value = accessedRoutes

    return accessedRoutes
  }

  /**
   * 递归过滤路由
   */
  function filterAsyncRoutes(routes: RouteRecordRaw[], permissions: string[]): RouteRecordRaw[] {
    const res: RouteRecordRaw[] = []

    routes.forEach(route => {
      const tmp = { ...route }

      // 检查路由权限
      if (hasPermission(permissions, tmp)) {
        // 递归处理子路由
        if (tmp.children) {
          tmp.children = filterAsyncRoutes(tmp.children, permissions)
        }
        res.push(tmp)
      }
    })

    return res
  }

  /**
   * 检查是否有权限访问路由
   */
  function hasPermission(permissions: string[], route: RouteRecordRaw): boolean {
    // 如果没有设置权限要求，则允许访问
    if (!route.meta?.permissions) {
      return true
    }

    // 超级管理员权限
    if (permissions.includes('*:*:*')) {
      return true
    }

    // 检查是否有任一所需权限
    const requiredPermissions = route.meta.permissions as string[]
    return requiredPermissions.some(permission => permissions.includes(permission))
  }

  /**
   * 重置路由
   */
  function resetRoutes() {
    routes.value = []
    dynamicRoutes.value = []
  }

  return {
    routes,
    dynamicRoutes,
    generateRoutes,
    resetRoutes
  }
})
