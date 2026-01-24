/**
 * Pinia Store 入口
 */
import type { App } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

export function setupStore(app: App) {
  app.use(pinia)
}

export default pinia

// 导出 stores
export { useAuthStore } from './auth'
export { usePermissionStore } from './permission'
