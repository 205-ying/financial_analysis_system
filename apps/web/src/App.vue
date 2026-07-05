<template>
  <el-config-provider :locale="zhCn">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </el-config-provider>
</template>

<script setup lang="ts">
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

// 初始化主题
const initTheme = () => {
  // 检查本地存储的主题偏好
  const savedTheme = localStorage.getItem('theme') || 'light'
  // 检查系统偏好
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

  if (savedTheme === 'dark' || (savedTheme === 'auto' && prefersDark)) {
    document.documentElement.setAttribute('data-theme', 'dark')
    document.documentElement.classList.add('dark-mode')
  } else {
    document.documentElement.setAttribute('data-theme', 'light')
    document.documentElement.classList.remove('dark-mode')
  }
}

// 在组件挂载时初始化主题
import { onMounted } from 'vue'
onMounted(() => {
  initTheme()
})
</script>

<style lang="scss">
// 页面过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--transition-duration-base) var(--transition-timing-function-base);
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 无障碍支持：焦点样式
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
  border-radius: var(--border-radius-sm);
}

// 使用设计系统的颜色变量定义滚动条样式
::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

::-webkit-scrollbar-track {
  background: var(--color-gray-100);
  border-radius: 5px;
}

::-webkit-scrollbar-thumb {
  background: var(--color-gray-400);
  border-radius: 5px;
  border: 2px solid var(--color-gray-100);

  &:hover {
    background: var(--color-gray-500);
  }

  &:active {
    background: var(--color-gray-600);
  }
}

// 暗色主题下的滚动条样式
[data-theme="dark"],
.dark-mode {
  ::-webkit-scrollbar-track {
    background: var(--color-gray-800);
  }

  ::-webkit-scrollbar-thumb {
    background: var(--color-gray-600);
    border-color: var(--color-gray-800);

    &:hover {
      background: var(--color-gray-500);
    }

    &:active {
      background: var(--color-gray-400);
    }
  }
}
</style>
