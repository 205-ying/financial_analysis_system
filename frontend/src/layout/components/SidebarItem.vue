<template>
  <div v-if="!item.meta?.hidden">
    <!-- 有子菜单 -->
    <el-sub-menu v-if="hasChildren" :index="resolvePath(item.path)">
      <template #title>
        <el-icon v-if="item.meta?.icon">
          <component :is="item.meta.icon" />
        </el-icon>
        <span>{{ item.meta?.title }}</span>
      </template>

      <sidebar-item
        v-for="child in item.children"
        :key="child.path"
        :item="child"
        :base-path="resolvePath(item.path)"
      />
    </el-sub-menu>

    <!-- 无子菜单 -->
    <el-menu-item v-else :index="resolvePath(item.path)">
      <el-icon v-if="item.meta?.icon">
        <component :is="item.meta.icon" />
      </el-icon>
      <template #title>
        <span>{{ item.meta?.title }}</span>
      </template>
    </el-menu-item>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { RouteRecordRaw } from 'vue-router'

interface Props {
  item: RouteRecordRaw
  basePath?: string
}

const props = defineProps<Props>()

// 是否有子菜单
const hasChildren = computed(() => {
  return props.item.children && props.item.children.length > 0
})

// 解析路径
const resolvePath = (routePath: string): string => {
  if (routePath.startsWith('/')) {
    return routePath
  }
  return props.basePath ? `${props.basePath}/${routePath}` : `/${routePath}`
}
</script>
