<template>
  <div class="empty-state">
    <el-icon :size="iconSize" :color="iconColor">
      <component :is="iconComponent" />
    </el-icon>
    <p class="empty-text">{{ text || defaultText }}</p>
    <slot>
      <el-button v-if="showAction" type="primary" size="small" @click="$emit('action')">
        {{ actionText }}
      </el-button>
    </slot>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Document, Search, FolderOpened, Box, DataBoard } from '@element-plus/icons-vue'
import type { Component } from 'vue'

export interface EmptyStateProps {
  /** 显示文本 */
  text?: string
  /** 图标类型 */
  iconType?: 'document' | 'search' | 'folder' | 'box' | 'dashboard' | 'nodata' | 'custom'
  /** 自定义图标组件 */
  customIcon?: Component
  /** 图标大小 */
  iconSize?: number
  /** 图标颜色 */
  iconColor?: string
  /** 是否显示操作按钮 */
  showAction?: boolean
  /** 操作按钮文本 */
  actionText?: string
}

const props = withDefaults(defineProps<EmptyStateProps>(), {
  text: '',
  iconType: 'nodata',
  iconSize: 64,
  iconColor: 'var(--color-gray-300)',
  showAction: false,
  actionText: '刷新数据'
})

const emit = defineEmits<{
  action: []
}>()

const defaultText = '暂无数据'

const iconComponent = computed(() => {
  if (props.customIcon) return props.customIcon

  switch (props.iconType) {
    case 'document': return Document
    case 'search': return Search
    case 'folder': return FolderOpened
    case 'box': return Box
    case 'dashboard': return DataBoard
    case 'nodata': return Box
    default: return Box
  }
})
</script>

<style scoped lang="scss">
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-8) var(--spacing-4);
  text-align: center;
  color: var(--color-text-tertiary);

  .empty-text {
    margin: var(--spacing-4) 0 var(--spacing-5);
    font-size: var(--font-size-base);
    line-height: var(--line-height-relaxed);
    max-width: 400px;
    color: var(--color-text-secondary);
  }

  :deep(.el-icon) {
    opacity: 0.6;
  }
}
</style>