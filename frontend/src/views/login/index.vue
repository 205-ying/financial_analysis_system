<template>
  <div class="login-container">
    <!-- 背景动态渐变色块 -->
    <div class="blob blob-1"></div>
    <div class="blob blob-2"></div>
    <div class="blob blob-3"></div>

    <div class="login-box glass-card">
      <div class="login-header">
        <h2>财务分析系统</h2>
        <p>Financial Analysis System</p>
      </div>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="loginRules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入用户名"
            prefix-icon="User"
            size="large"
            clearable
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            prefix-icon="Lock"
            size="large"
            show-password
            clearable
          />
        </el-form-item>

        <el-form-item>
          <el-button
            :loading="loading"
            type="primary"
            size="large"
            class="login-button"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-tips">
        <p>测试账号：</p>
        <p>超级管理员：admin / Admin@123</p>
        <p>门店经理：manager / Manager@123</p>
        <p>收银员：cashier / Cashier@123</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import type { LoginRequest } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 登录表单
const loginFormRef = ref<FormInstance>()
const loginForm = reactive<LoginRequest>({
  username: '',
  password: ''
})

// 表单验证规则
const loginRules = reactive<FormRules<LoginRequest>>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' }
  ]
})

// 登录加载状态
const loading = ref(false)

/**
 * 处理登录
 */
const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true

      try {
        await authStore.login(loginForm)
        ElMessage.success('登录成功')

        // 获取重定向路径
        const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
        await router.push(redirect || '/')
      } catch (error) {
        ElMessage.error('登录失败，请检查账号密码或稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  position: relative;
  /* 更加深邃有立体感的底色与几何网格 */
  background-color: #F1F5F9;
  background-image: 
    radial-gradient(at 0% 0%, hsla(253,16%,7%,0.05) 0, transparent 50%), 
    radial-gradient(at 50% 0%, hsla(225,39%,30%,0.05) 0, transparent 50%), 
    radial-gradient(at 100% 0%, hsla(339,49%,30%,0.05) 0, transparent 50%);
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    z-index: 0;
    /* 前卫网格风背景 */
    background-size: 40px 40px;
    background-image: 
      linear-gradient(to right, rgba(99, 102, 241, 0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(99, 102, 241, 0.05) 1px, transparent 1px);
    mask-image: radial-gradient(circle at center, black 40%, transparent 80%);
    -webkit-mask-image: radial-gradient(circle at center, black 40%, transparent 80%);
  }
}

/* 动态三维几何渐变色块 */
.blob {
  position: absolute;
  filter: blur(80px);
  z-index: 0;
  border-radius: 50%;
  animation: breathe 10s infinite alternate cubic-bezier(0.4, 0, 0.2, 1);
}

.blob-1 {
  width: 50vw;
  height: 50vw;
  max-width: 600px;
  max-height: 600px;
  background: linear-gradient(135deg, rgba(67, 56, 202, 0.5) 0%, rgba(129, 140, 248, 0.8) 100%);
  top: -10%;
  left: -10%;
  animation-duration: 12s;
}

.blob-2 {
  width: 40vw;
  height: 40vw;
  max-width: 500px;
  max-height: 500px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.7) 0%, rgba(99, 102, 241, 0.4) 100%);
  bottom: -15%;
  right: -5%;
  animation-duration: 14s;
  animation-delay: 2s;
}

.blob-3 {
  width: 30vw;
  height: 30vw;
  max-width: 400px;
  max-height: 400px;
  background: linear-gradient(135deg, rgba(224, 231, 255, 0.9) 0%, rgba(79, 70, 229, 0.3) 100%);
  top: 30%;
  left: 50%;
  animation-duration: 16s;
  animation-delay: 4s;
  transform: translateX(-50%);
}

@keyframes breathe {
  0% {
    transform: translate(0, 0) scale(1) rotate(0deg);
  }
  50% {
    transform: translate(30px, -30px) scale(1.05) rotate(10deg);
  }
  100% {
    transform: translate(-20px, 20px) scale(0.95) rotate(-5deg);
  }
}

.login-box {
  width: 420px;
  padding: 40px;
  position: relative;
  z-index: 1;
}

.glass-card {
  /* 极致毛玻璃面板材质 */
  background: rgba(255, 255, 255, 0.65);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  
  /* 极细的内发光边框 */
  border: 1px solid rgba(255, 255, 255, 0.4);
  
  /* 发散柔和的深蓝色/紫色系弥散阴影 */
  box-shadow: 
    0 24px 48px -12px rgba(67, 56, 202, 0.25), 
    0 0 24px rgba(99, 102, 241, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;

  h2 {
    margin: 0 0 12px;
    font-size: 28px;
    font-weight: 700;
    color: var(--color-text-primary, #0F172A);
    letter-spacing: -0.5px;
  }

  p {
    margin: 0;
    font-size: 14px;
    color: var(--color-text-secondary, #64748B);
  }
}

.login-form {
  .el-form-item {
    margin-bottom: 24px;
  }
  
  // 覆盖 element-plus 的输入框默认样式以适配毛玻璃风
  :deep(.el-input) {
    width: 100%;
    
    .el-input__wrapper {
      background-color: rgba(255, 255, 255, 0.7) !important;
      border: none !important;
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 1), 0 2px 6px rgba(0,0,0, 0.02) !important;
      border-radius: 12px;
      padding: 4px 12px;
      transition: all 0.3s ease;
      
      &.is-focus {
        background-color: rgba(255, 255, 255, 0.9) !important;
        box-shadow: inset 0 0 0 1px var(--color-primary, #4338CA), 0 4px 12px rgba(67, 56, 202, 0.08) !important;
      }
    }

    .el-input__inner {
      height: 38px;
      color: var(--color-text-primary, #0F172A);
    }

    // prefix icon size overrides
    .el-input__icon,
    .el-input__prefix {
      font-size: 18px !important;
      color: var(--color-text-secondary, #64748B);
    }
  }

  .login-button {
    width: 100%;
    height: 48px;
    margin-top: 10px;
    padding: 0 24px;
    border-radius: 9999px; // 完全圆角 pill-shaped
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 1px;
    background: linear-gradient(135deg, #4338CA 0%, #6366F1 100%);
    border: none;
    color: white;
    box-shadow: 0 4px 14px rgba(67, 56, 202, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;

    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: -100%;
      width: 50%;
      height: 100%;
      background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 100%);
      transform: skewX(-25deg);
      transition: all 0.5s ease;
    }

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(67, 56, 202, 0.4);
      background: linear-gradient(135deg, #3730A3 0%, #4F46E5 100%);
      
      &::after {
        left: 200%; // 流水光影动效能通过过渡实现
      }
    }
    
    &:active {
      transform: translateY(0);
      box-shadow: 0 4px 10px rgba(67, 56, 202, 0.3);
    }
  }
}

.login-tips {
  margin-top: 24px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  border-radius: 12px;
  font-size: 13px;
  color: var(--color-text-secondary, #64748B);
  line-height: 1.8;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.6);
  
  p {
    margin: 0;
    
    &:first-child {
      font-weight: 600;
      color: var(--color-text-primary, #0F172A);
      margin-bottom: 4px;
    }
  }
}

@media (max-width: 600px) {
  .login-box {
    width: 92%;
    padding: 24px;
    margin: 20px;
  }

  .login-header h2 { font-size: 24px; }
  
  .login-form :deep(.el-input) {
    .el-input__icon, .el-input__prefix { font-size: 16px !important; }
  }
}
</style>
