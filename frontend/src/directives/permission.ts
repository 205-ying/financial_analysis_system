/**
 * 权限控制指令
 */
import type { App, Directive, DirectiveBinding } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * 权限指令
 * 用法：v-permission="'user:create'" 或 v-permission="['user:create', 'user:update']"
 */
const permissionDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    const { value } = binding
    if (!value) return

    const authStore = useAuthStore()

    let hasPermission = false

    if (typeof value === 'string') {
      // 单个权限
      hasPermission = authStore.hasPermission(value)
    } else if (Array.isArray(value)) {
      // 多个权限（满足任意一个即可）
      hasPermission = authStore.hasAnyPermission(value)
    }

    // 如果没有权限，移除元素
    if (!hasPermission) {
      el.parentNode?.removeChild(el)
    }
  }
}

/**
 * 权限指令（全部满足）
 * 用法：v-permission-all="['user:create', 'user:update']"
 */
const permissionAllDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    const { value } = binding
    if (!value || !Array.isArray(value)) return

    const authStore = useAuthStore()

    // 检查是否拥有所有权限
    const hasPermission = authStore.hasPermissions(value)

    // 如果没有权限，移除元素
    if (!hasPermission) {
      el.parentNode?.removeChild(el)
    }
  }
}

/**
 * 注册权限指令
 */
export function setupPermissionDirective(app: App) {
  app.directive('permission', permissionDirective)
  app.directive('permission-all', permissionAllDirective)
}

export default {
  install: setupPermissionDirective
}
