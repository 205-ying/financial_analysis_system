<template>
  <div v-if="show" class="loading-spinner" :class="{ 'fullscreen': fullscreen, 'inline': !fullscreen }">
    <div class="spinner-container">
      <el-icon class="spinning" :size="size" :color="color">
        <Loading />
      </el-icon>
      <span v-if="text" class="loading-text">{{ text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Loading } from '@element-plus/icons-vue'

export interface LoadingSpinnerProps {
  /** 是否显示 */
  show: boolean
  /** 加载文本 */
  text?: string
  /** 图标大小 */
  size?: number
  /** 图标颜色 */
  color?: string
  /** 是否全屏显示 */
  fullscreen?: boolean
  /** 背景颜色 */
  backgroundColor?: string
  /** 是否显示遮罩 */
  showOverlay?: boolean
  /** 自定义类名 */
  customClass?: string
}

withDefaults(defineProps<LoadingSpinnerProps>(), {
  show: false,
  text: '',
  size: 40,
  color: 'var(--color-primary)',
  fullscreen: false,
  backgroundColor: 'rgba(var(--color-bg-primary), 0.8)',
  showOverlay: true,
  customClass: ''
})

// 生成唯一的ID用于全屏模式（保留供未来使用）
// const spinnerId = `loading-spinner-${Math.random().toString(36).substr(2, 9)}`
</script>

<style scoped lang="scss">
.loading-spinner {
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: var(--z-index-modal);

  &.fullscreen {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: v-bind(backgroundColor);
    backdrop-filter: blur(4px);

    .spinner-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: var(--spacing-4);
      padding: var(--spacing-6);
      background-color: var(--color-white);
      border-radius: var(--border-radius-lg);
      box-shadow: var(--shadow-lg);
      border: 1px solid var(--color-border-light);
    }
  }

  &.inline {
    position: relative;
    min-height: 100px;

    .spinner-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: var(--spacing-3);
      padding: var(--spacing-5);
    }
  }

  .spinning {
    animation: spin 1s linear infinite;

    @keyframes spin {
      0% {
        transform: rotate(0deg);
      }
      100% {
        transform: rotate(360deg);
      }
    }
  }

  .loading-text {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    font-weight: var(--font-weight-medium);
    text-align: center;
  }
}

// 暗色主题适配
[data-theme="dark"],
.dark-mode {
  .loading-spinner {
    &.fullscreen {
      .spinner-container {
        background-color: var(--color-gray-800);
        border-color: var(--color-gray-700);
      }
    }

    .loading-text {
      color: var(--color-gray-300);
    }
  }
}
</style>