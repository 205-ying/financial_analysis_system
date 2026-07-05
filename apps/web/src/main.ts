import { createApp } from 'vue'
// 首先导入 Element Plus 样式
import 'element-plus/dist/index.css'
// 导入 UnoCSS 样式
import 'uno.css'
// 然后导入全局设计系统样式（会覆盖 Element Plus 默认样式）
import '@/styles/index.scss'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import { setupStore } from './stores'
import { setupRouter } from './router'
import { setupPermissionDirective } from '@/directives'
import { registerEChartsThemes } from '@/config/echarts-theme'

const app = createApp(App)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册 ECharts 主题
registerEChartsThemes()

// 注册 Pinia 状态管理
setupStore(app)

// 注册路由
setupRouter(app)

// 注册权限指令
setupPermissionDirective(app)

// 挂载应用
app.mount('#app')
