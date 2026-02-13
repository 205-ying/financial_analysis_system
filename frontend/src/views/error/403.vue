<template>
  <div class="error-page">
    <div class="error-content">
      <el-icon class="error-icon" :size="120" color="#409eff">
        <Lock />
      </el-icon>
      <h1 class="error-title">403</h1>
      <p class="error-message">抱歉，您无权访问此页面</p>
      <el-button type="primary" @click="handleGoBack">返回上一页</el-button>
      <el-button @click="handleGoHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'

const router = useRouter()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

const handleGoBack = () => {
  // 如果有历史记录就返回，否则跳转首页
  if (window.history.length > 1) {
    router.back()
  } else {
    handleGoHome()
  }
}

const handleGoHome = async () => {
  try {
    // 检查是否已登录
    if (!authStore.isLoggedIn) {
      router.push('/login')
      return
    }

    // 检查是否已生成动态路由
    if (!permissionStore.routes || permissionStore.routes.length === 0) {
      // 如果没有生成路由，先生成路由
      await authStore.getUserInfo()
      const accessRoutes = permissionStore.generateRoutes()
      
      // 找到第一个可访问的路由
      const firstRoute = accessRoutes.find(route => !route.meta?.hidden && route.path !== '/')
      if (firstRoute) {
        router.push(firstRoute.path)
      } else {
        // 如果没有任何可访问路由，跳转到登录页
        router.push('/login')
      }
    } else {
      // 已有路由，直接跳转首页
      router.push('/')
    }
  } catch {
    // 出错时跳转到登录页
    router.push('/login')
  }
}
</script>

<style scoped lang="scss">
.error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.error-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px;
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);

  .error-icon {
    margin-bottom: 30px;
    animation: bounce 2s infinite;
  }

  .error-title {
    font-size: 80px;
    font-weight: 700;
    color: #333;
    margin: 0 0 20px;
  }

  .error-message {
    font-size: 18px;
    color: #666;
    margin: 0 0 40px;
  }

  .el-button {
    margin: 0 10px;
  }
}

@keyframes bounce {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}
</style>
