<template>
  <div class="layout-container">
    <el-container>
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
        <div class="logo">
          <span v-if="!isCollapse" class="logo-title">财务分析系统</span>
          <span v-else class="logo-icon">FA</span>
        </div>

        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :unique-opened="true"
          :collapse-transition="false"
          router
          class="sidebar-menu"
        >
          <sidebar-item
            v-for="menuRoute in permissionRoutes"
            :key="menuRoute.path"
            :item="menuRoute"
            :base-path="menuRoute.path"
          />
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-container class="layout-content">
        <!-- 顶部栏 -->
        <el-header class="layout-header">
          <div class="header-left">
            <el-icon class="collapse-icon" @click="toggleCollapse">
              <Fold v-if="!isCollapse" />
              <Expand v-else />
            </el-icon>

            <!-- 面包屑 -->
            <el-breadcrumb separator="/" class="breadcrumb">
              <el-breadcrumb-item
                v-for="(item, index) in breadcrumbs"
                :key="index"
                :to="item.path"
              >
                {{ item.title }}
              </el-breadcrumb-item>
            </el-breadcrumb>
          </div>

          <div class="header-right">
            <!-- 用户信息 -->
            <el-dropdown @command="handleCommand">
              <div class="user-info">
                <el-avatar :size="32" :icon="UserFilled" />
                <span class="username">{{ username }}</span>
                <el-icon><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <!-- 内容区 -->
        <el-main class="layout-main">
          <router-view v-slot="{ Component }">
            <transition name="fade-transform" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { Fold, Expand, UserFilled, ArrowDown } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'
import SidebarItem from './components/SidebarItem.vue'

const route = useRoute()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 当前激活的菜单
const activeMenu = computed(() => route.path)

// 用户名
const username = computed(() => authStore.username)

// 权限路由
const permissionRoutes = computed(() => {
  return permissionStore.routes.filter(route => !route.meta?.hidden)
})

// 面包屑
const breadcrumbs = ref<Array<{ title: string; path: string }>>([])

/**
 * 获取面包屑
 */
const getBreadcrumbs = () => {
  const matched = route.matched.filter(item => item.meta?.title)
  breadcrumbs.value = matched.map(item => ({
    title: item.meta?.title as string,
    path: item.path
  }))
}

// 监听路由变化，更新面包屑
watch(
  () => route.path,
  () => {
    getBreadcrumbs()
  },
  { immediate: true }
)

/**
 * 切换侧边栏折叠状态
 */
const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

/**
 * 处理下拉菜单命令
 */
const handleCommand = async (command: string) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(async () => {
        await authStore.logout()
      })
      .catch(() => {
        // 用户取消
      })
  }
}
</script>

<style scoped lang="scss">
// 导入变量（通过vite.config.ts全局导入）
// @use '@/styles/variables/borders' as *;
// @use '@/styles/variables/spacing' as *;
// @use '@/styles/variables/typography' as *;
// @use '@/styles/variables/shadows' as *;
// @use '@/styles/variables/animations' as *;

// 布局容器
.layout-container {
  height: 100vh;
  overflow: hidden;
  display: flex;
  background: var(--color-bg-secondary);

  :deep(.el-container) {
    height: 100%;
  }
}

// 侧边栏
.layout-aside {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-white);
  transition: width $duration-base $easing-ease-in-out;
  box-shadow: 1px 0 0 0 rgba(0, 0, 0, 0.03);
  z-index: $z-index-sticky;

  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 54px;
    background: var(--color-white);
    color: var(--color-text-primary);
    font-size: $font-size-lg;
    font-weight: $font-weight-bold;
    padding: 0 $spacing-4;
    transition: all $duration-base $easing-ease-in-out;
    overflow: hidden;

    .logo-title {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      letter-spacing: $letter-spacing-wide;
    }

    .logo-icon {
      font-size: $font-size-xl;
      font-weight: $font-weight-bold;
      background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
  }

  // 侧边栏菜单
  :deep(.sidebar-menu) {
    flex: 1;
    border-right: none;
    overflow-y: auto;
    overflow-x: hidden;
    background-color: transparent !important;
    padding: $spacing-2 0;

    .el-menu-item,
    .el-sub-menu__title {
      height: 44px;
      line-height: 44px;
      margin: $spacing-1 $spacing-3;
      border-radius: $border-radius-md;
      transition: all $duration-base $easing-ease-in-out;
      color: var(--color-text-secondary) !important;
      border-left: 3px solid transparent; // 占位保持稳定

      &:hover {
        background-color: rgba(67, 56, 202, 0.03) !important;
        color: var(--color-primary) !important;
      }

      &.is-active {
        background: rgba(67, 56, 202, 0.05) !important;
        color: var(--color-primary) !important;
        font-weight: $font-weight-bold;
        border-left: 3px solid var(--color-primary);

        .el-sub-menu__title {
          color: var(--color-primary) !important;
        }
      }

      .el-icon {
        font-size: $font-size-lg;
        margin-right: $spacing-3;
        color: inherit !important;
      }
    }

    .el-sub-menu {
      .el-menu {
        background-color: transparent !important;
        padding-left: $spacing-2;

        .el-menu-item {
          margin: $spacing-1 $spacing-2;
          padding-left: $spacing-8 !important;
        }
      }
    }
  }

  // 滚动条样式
  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background-color: rgba(var(--color-primary), 0.3);
    border-radius: $border-radius-full;
  }
}

// 主内容区
.layout-content {
  height: 100vh;
  min-width: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex: 1;
}

// 顶部栏
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 $spacing-6;
  background: transparent; // 无缝融入右侧主区域
  border-bottom: none; // 去除坚硬的border-bottom
  height: 54px; // 压缩至更紧凑
  z-index: $z-index-fixed;

  .header-left {
    display: flex;
    align-items: center;
    gap: $spacing-4;

    .collapse-icon {
      font-size: $font-size-xl;
      cursor: pointer;
      color: var(--color-text-secondary);
      padding: $spacing-1;
      border-radius: $border-radius-md;
      transition: all $duration-base $easing-ease-in-out;

      &:hover {
        color: var(--color-primary);
        background-color: rgba(var(--color-primary), 0.1);
      }

      &:active {
        transform: scale(0.95);
      }
    }

    .breadcrumb {
      font-size: $font-size-sm;
      color: var(--color-text-secondary);

      :deep(.el-breadcrumb__inner) {
        transition: color $duration-fast $easing-ease-in-out;

        &:hover {
          color: var(--color-primary);
        }
      }

      :deep(.el-breadcrumb__separator) {
        color: var(--color-text-tertiary);
      }
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: $spacing-2;
      cursor: pointer;
      padding: $spacing-1 $spacing-2;
      border-radius: $border-radius-full;
      transition: all $duration-base $easing-ease-in-out;
      background: transparent; // 幽灵无边框

      &:hover {
        background-color: rgba(0, 0, 0, 0.03); // 极简幽灵渐变
        transform: translateY(-1px);
      }

      .username {
        font-size: $font-size-sm;
        font-weight: $font-weight-medium;
        color: var(--color-text-secondary);
        max-width: 120px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .el-icon {
        color: var(--color-text-tertiary);
        transition: transform $duration-base $easing-ease-in-out;
      }

      &:hover .el-icon {
        transform: rotate(180deg);
      }
    }
  }
}

// 主内容区域
.layout-main {
  flex: 1;
  min-height: 0;
  background: transparent; // 调整为透明，因为外层 layout-container 已经是 --color-bg-secondary
  padding: 0 $spacing-6 $spacing-6;
  overflow-y: auto;
  position: relative;
}

// 页面过渡动画
.fade-transform {
  &-enter-active,
  &-leave-active {
    transition: all $duration-base $easing-ease-in-out;
  }

  &-enter-from {
    opacity: 0;
    transform: translateY(-20px);
    filter: blur(4px);
  }

  &-leave-to {
    opacity: 0;
    transform: translateY(20px);
    filter: blur(4px);
  }
}

// 响应式设计
@media (max-width: $breakpoint-md) {
  .layout-header {
    padding: 0 $spacing-4;
    height: 56px;

    .header-left {
      gap: $spacing-3;

      .collapse-icon {
        font-size: $font-size-lg;
      }

      .breadcrumb {
        font-size: $font-size-xs;
      }
    }

    .header-right {
      .user-info {
        padding: $spacing-1 $spacing-2;

        .username {
          max-width: 80px;
          font-size: $font-size-xs;
        }
      }
    }
  }

  .layout-main {
    padding: $spacing-4;
  }

  .layout-aside {
    .logo {
      height: 56px;
      font-size: $font-size-base;

      .logo-icon {
        font-size: $font-size-lg;
      }
    }

    :deep(.sidebar-menu) {
      .el-menu-item,
      .el-sub-menu__title {
        height: 40px;
        line-height: 40px;
        margin: $spacing-1 $spacing-2;
        font-size: $font-size-sm;

        .el-icon {
          font-size: $font-size-base;
          margin-right: $spacing-2;
        }
      }
    }
  }
}

@media (max-width: $breakpoint-sm) {
  .layout-header {
    padding: 0 $spacing-3;
    height: 52px;

    .header-left {
      .breadcrumb {
        display: none;
      }
    }

    .header-right {
      .user-info {
        .username {
          display: none;
        }
      }
    }
  }

  .layout-main {
    padding: $spacing-3;
  }

  .layout-aside {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: $z-index-modal;
    box-shadow: $shadow-xl;

    &:not(.is-collapse) {
      width: 220px !important;
    }

    &.is-collapse {
      width: 64px !important;
    }
  }

  .layout-content {
    margin-left: 0;
  }
}

// 暗色主题适配
[data-theme="dark"],
.dark-mode {
  .layout-container {
    background: var(--color-bg-primary);
  }

  .layout-aside {
    background: linear-gradient(180deg, var(--color-gray-900), var(--color-gray-850));
    border-right: 1px solid var(--color-gray-700);

    .logo {
      background: linear-gradient(90deg, var(--color-primary-dark), var(--color-primary-darker));
    }

    :deep(.sidebar-menu) {
      .el-menu-item,
      .el-sub-menu__title {
        color: var(--color-gray-300) !important;

        &:hover {
          background-color: rgba(var(--color-primary), 0.2) !important;
          color: var(--color-white) !important;
        }

        &.is-active {
          background: linear-gradient(90deg, rgba(var(--color-primary), 0.3), rgba(var(--color-primary), 0.2)) !important;
          color: var(--color-primary-light) !important;
        }
      }
    }
  }

  .layout-header {
    background: var(--color-gray-800);
    border-bottom-color: var(--color-gray-700);

    .header-left {
      .collapse-icon {
        color: var(--color-gray-300);

        &:hover {
          color: var(--color-primary-light);
          background-color: rgba(var(--color-primary), 0.2);
        }
      }

      .breadcrumb {
        color: var(--color-gray-300);

        :deep(.el-breadcrumb__inner) {
          &:hover {
            color: var(--color-primary-light);
          }
        }
      }
    }

    .header-right {
      .user-info {
        &:hover {
          background-color: var(--color-gray-700);
        }

        .username {
          color: var(--color-gray-200);
        }
      }
    }
  }

  .layout-main {
    background: linear-gradient(135deg, var(--color-gray-850), var(--color-gray-800));
  }
}

// 打印样式
@media print {
  .layout-aside,
  .layout-header {
    display: none !important;
  }

  .layout-content {
    margin: 0 !important;
  }

  .layout-main {
    padding: 0 !important;
    background: transparent !important;
  }
}
</style>
