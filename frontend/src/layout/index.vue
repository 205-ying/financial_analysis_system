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
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
          router
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
.layout-container {
  height: 100vh;
  overflow: hidden;

  :deep(.el-container) {
    height: 100%;
  }
}

.layout-aside {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #304156;
  transition: width 0.3s;

  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 60px;
    background-color: #2b2f3a;
    color: white;
    font-size: 18px;
    font-weight: 600;

    .logo-icon {
      font-size: 24px;
    }
  }

  :deep(.el-menu) {
    flex: 1;
    border-right: none;
    overflow-y: auto;
    overflow-x: hidden;
  }
}

.layout-content {
  height: 100vh;
  min-width: 0;
  overflow: hidden;
}

.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: white;
  border-bottom: 1px solid #e6e6e6;

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;

    .collapse-icon {
      font-size: 20px;
      cursor: pointer;
      transition: color 0.3s;

      &:hover {
        color: #409eff;
      }
    }

    .breadcrumb {
      font-size: 14px;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      padding: 5px 10px;
      border-radius: 4px;
      transition: background-color 0.3s;

      &:hover {
        background-color: #f5f7fa;
      }

      .username {
        font-size: 14px;
        color: #333;
      }
    }
  }
}

.layout-main {
  min-height: 0;
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

// 过渡动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s;
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
