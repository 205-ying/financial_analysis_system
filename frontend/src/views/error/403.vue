<template>
  <div class="error-page">
    <div class="error-content">
      <el-icon class="error-icon" :size="120" color="#409eff">
        <Lock />
      </el-icon>
      <h1 class="error-title">403</h1>
      <p class="error-message">抱歉，您无权访问此页面</p>
      <el-button type="primary" @click="goBack">返回上一页</el-button>
      <el-button @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Lock } from '@element-plus/icons-vue'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
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
