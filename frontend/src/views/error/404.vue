<template>
  <div class="error-page">
    <div class="error-content">
      <el-icon class="error-icon" :size="120" color="#f56c6c">
        <QuestionFilled />
      </el-icon>
      <h1 class="error-title">404</h1>
      <p class="error-message">抱歉，您访问的页面不存在</p>
      <el-button type="primary" @click="goBack">返回上一页</el-button>
      <el-button @click="goHome">返回首页</el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { QuestionFilled } from '@element-plus/icons-vue'

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
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
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
    animation: shake 2s infinite;
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

@keyframes shake {
  0%,
  100% {
    transform: rotate(0deg);
  }
  25% {
    transform: rotate(-10deg);
  }
  75% {
    transform: rotate(10deg);
  }
}
</style>
