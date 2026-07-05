/**
 * 权限管理 Store
 */
import { defineStore } from 'pinia'
import { ref, markRaw } from 'vue'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from './auth'
import { DYNAMIC_ROUTE_CONFIGS, PERMISSIONS, type DynamicRouteConfig } from '@/config'
import {
  DataAnalysis,
  Document,
  Money,
  TrendCharts,
  List,
  Upload,
  Setting,
  Dish,
  Wallet
} from '@element-plus/icons-vue'

const iconMap = {
  DataAnalysis,
  Document,
  Money,
  TrendCharts,
  List,
  Upload,
  Setting,
  Dish,
  Wallet,
} as const

function buildRoutesFromConfig(configs: DynamicRouteConfig[]): RouteRecordRaw[] {
  return configs.map((route) => {
    const { children, meta, components, component, redirect, ...rest } = route as DynamicRouteConfig & {
      components?: RouteRecordRaw['components'] | null
      component?: RouteRecordRaw['component'] | null
      redirect?: RouteRecordRaw['redirect']
    }

    const builtRoute = {
      ...rest,
      meta: meta
        ? {
            ...meta,
            icon: meta.iconKey ? markRaw(iconMap[meta.iconKey as keyof typeof iconMap]) : undefined,
          }
        : undefined,
    } as RouteRecordRaw

    if (redirect !== undefined) {
      builtRoute.redirect = redirect
    }
    if (component) {
      builtRoute.component = component
    }
    if (components) {
      builtRoute.components = components
      if (!children) {
        builtRoute.children = []
      }
    }
    if (children) {
      builtRoute.children = buildRoutesFromConfig(children)
    }

    return builtRoute
  })
}

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

    const asyncRoutes = buildRoutesFromConfig(DYNAMIC_ROUTE_CONFIGS)

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
    if (permissions.includes(PERMISSIONS.SUPER_ADMIN)) {
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
