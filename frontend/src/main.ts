import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import { setupStore } from './stores'
import { setupRouter } from './router'
import { setupPermissionDirective } from '@/directives'

const app = createApp(App)

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册 Element Plus
app.use(ElementPlus)

// 注册 Pinia 状态管理
setupStore(app)

// 注册路由
setupRouter(app)

// 注册权限指令
setupPermissionDirective(app)

// 挂载应用
app.mount('#app')
