<template>
  <div class="login-page">
    <aside class="login-rail">
      <div class="brand-block">
        <span class="brand-mark">
          <el-icon><CoffeeCup /></el-icon>
        </span>
        <div>
          <h1>财务分析系统</h1>
          <p>Restaurant Finance Console</p>
        </div>
      </div>
    </aside>

    <main class="login-main">
      <section class="login-card">
        <div class="form-head">
          <p>财务驾驶舱</p>
          <h2>登录到今日经营</h2>
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
              :prefix-icon="User"
              placeholder="用户名"
              size="large"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              :prefix-icon="Lock"
              type="password"
              placeholder="密码"
              size="large"
              show-password
              clearable
            />
          </el-form-item>

          <el-button
            :loading="loading"
            type="primary"
            size="large"
            class="login-button"
            :icon="Key"
            @click="handleLogin"
          >
            {{ loading ? '登录中' : '进入系统' }}
          </el-button>
        </el-form>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import {
  CoffeeCup,
  Key,
  Lock,
  User,
} from '@element-plus/icons-vue'

import { useAuthStore } from '@/stores/auth'
import type { LoginRequest } from '@/types'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()
const loginForm = reactive<LoginRequest>({
  username: '',
  password: '',
})

const loginRules = reactive<FormRules<LoginRequest>>({
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 50, message: '用户名长度在 2 到 50 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度在 6 到 50 个字符', trigger: 'blur' },
  ],
})

const loading = ref(false)

async function handleLogin() {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true

    try {
      await authStore.login(loginForm)
      ElMessage.success('登录成功')

      const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
      await router.push(redirect || '/')
    } catch {
      ElMessage.error('登录失败，请检查账号密码或稍后重试')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: minmax(360px, 560px) minmax(420px, 1fr);
  background:
    linear-gradient(90deg, #071114 0 36%, transparent 36%),
    repeating-linear-gradient(0deg, rgba(51, 45, 40, 0.035) 0 1px, transparent 1px 42px),
    #F5F1EA;
  color: #332D28;
  overflow: hidden;
}

.login-rail {
  position: relative;
  min-height: 100vh;
  padding: 32px;
  background:
    linear-gradient(150deg, rgba(18, 33, 34, 0.96), rgba(4, 14, 17, 0.98)),
    #071114;
  color: #F7EFE2;
  display: grid;
  align-content: center;
  gap: 18px;

  &::after {
    content: '';
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
      linear-gradient(90deg, rgba(255, 255, 255, 0.055) 1px, transparent 1px),
      linear-gradient(0deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);
    background-size: 40px 40px;
    opacity: 0.35;
  }

  > * {
    position: relative;
    z-index: 1;
  }
}

.brand-block {
  display: flex;
  align-items: center;
  gap: 14px;

  h1 {
    margin: 0;
    color: #F7EFE2;
    font-size: 21px;
    line-height: 1.1;
    font-weight: 900;
  }

  p {
    margin: 6px 0 0;
    color: rgba(247, 239, 226, 0.58);
    font-size: 12px;
    letter-spacing: 0;
  }
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 8px;
  color: #F2C776;
  background: rgba(242, 199, 118, 0.12);
  border: 1px solid rgba(242, 199, 118, 0.28);
  font-size: 25px;
}

.login-main {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 40px;
}

.login-card {
  width: min(440px, 100%);
  padding: 34px;
  border-radius: 8px;
  background: rgba(255, 253, 249, 0.96);
  border: 1px solid #E4DED5;
  box-shadow: 0 18px 44px rgba(51, 45, 40, 0.12);
}

.form-head {
  margin-bottom: 26px;

  p {
    margin: 0 0 8px;
    color: #A66F17;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 0;
  }

  h2 {
    margin: 0;
    color: #17110D;
    font-size: 28px;
    line-height: 1.16;
    font-weight: 900;
  }
}

.login-form {
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }

  :deep(.el-input__wrapper) {
    min-height: 46px;
    border-radius: 6px;
    background: #FFFDF9;
    border: 1px solid #D7CEC2;
    box-shadow: none;
    padding: 0 13px;

    &.is-focus {
      border-color: #C81E1E;
      box-shadow: 0 0 0 3px rgba(200, 30, 30, 0.11);
    }
  }

  :deep(.el-input__inner) {
    color: #332D28;
    font-weight: 700;
  }

  :deep(.el-input__prefix) {
    color: #A66F17;
  }
}

.login-button {
  width: 100%;
  height: 48px;
  margin-top: 4px;
  border-radius: 6px;
  font-weight: 900;
  background: #C81E1E;
  border-color: #C81E1E;
  box-shadow: 0 10px 22px rgba(200, 30, 30, 0.2);

  &:hover,
  &:focus {
    background: #A91419;
    border-color: #A91419;
  }
}

@media (max-width: 980px) {
  .login-page {
    grid-template-columns: 1fr;
    background: #F5F1EA;
  }

  .login-rail {
    min-height: auto;
    padding: 24px;
  }

  .login-main {
    min-height: auto;
    padding: 28px 18px;
    place-items: start center;
  }
}

@media (max-width: 560px) {
  .login-rail {
    display: none;
  }

  .login-main {
    min-height: 100vh;
  }

  .login-card {
    padding: 24px;
  }

}
</style>
