<template>
  <div class="layout-shell" :class="{ 'is-collapsed': isCollapse }">
    <aside class="layout-aside">
      <div class="brand">
        <div class="brand-mark">
          <el-icon><CoffeeCup /></el-icon>
        </div>
        <div v-if="!isCollapse" class="brand-copy">
          <span class="brand-title">财务分析系统</span>
          <span class="brand-subtitle">Restaurant Finance</span>
        </div>
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

      <button class="collapse-dock" type="button" @click="toggleCollapse">
        <el-icon>
          <Expand v-if="isCollapse" />
          <Fold v-else />
        </el-icon>
        <span v-if="!isCollapse">收起菜单</span>
      </button>
    </aside>

    <section class="layout-workspace">
      <header class="layout-header">
        <div class="header-left">
          <div class="breadcrumbs">
            <template v-for="(item, index) in breadcrumbs" :key="item.path || index">
              <span v-if="index > 0" class="breadcrumb-separator">/</span>
              <span class="breadcrumb-item">{{ item.title }}</span>
            </template>
          </div>
          <span class="header-context">今日经营</span>
        </div>

        <div class="header-actions">
          <el-date-picker
            v-model="globalRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="~"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            :prefix-icon="Calendar"
            class="header-date"
          />

          <el-select v-model="storeScope" class="header-select" placeholder="全部门店">
            <el-option label="全部门店" value="all" />
            <el-option label="华东区域" value="east" />
            <el-option label="重点门店" value="focus" />
          </el-select>

          <el-button class="header-icon-btn" :icon="Download" @click="handleExport">导出</el-button>
          <el-button class="header-round-btn" :icon="Bell" circle />

          <el-dropdown @command="handleCommand">
            <button class="user-chip" type="button">
              <el-avatar :size="34" :icon="UserFilled" />
              <span class="user-meta">
                <strong>{{ username || '张伟' }}</strong>
                <small>{{ roleLabel }}</small>
              </span>
              <el-icon><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowDown,
  Bell,
  Calendar,
  CoffeeCup,
  Download,
  Expand,
  Fold,
  SwitchButton,
  UserFilled,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { usePermissionStore } from '@/stores/permission'
import SidebarItem from './components/SidebarItem.vue'

const route = useRoute()
const authStore = useAuthStore()
const permissionStore = usePermissionStore()

const isCollapse = ref(false)
const globalRange = ref<[string, string]>(['2024-05-01', '2024-05-31'])
const storeScope = ref('all')

const activeMenu = computed(() => route.path)
const username = computed(() => authStore.username)
const roleLabel = computed(() => {
  if (authStore.userInfo?.is_superuser) return '财务总监'
  return authStore.roles?.[0] || '经营分析'
})

const permissionRoutes = computed(() => {
  return permissionStore.routes.filter(route => !route.meta?.hidden)
})

const breadcrumbs = ref<Array<{ title: string; path: string }>>([])

const getBreadcrumbs = () => {
  const matched = route.matched.filter(item => item.meta?.title)
  breadcrumbs.value = matched.length
    ? matched.map(item => ({
        title: item.meta?.title as string,
        path: item.path,
      }))
    : [{ title: '财务驾驶舱', path: '/' }]
}

watch(
  () => route.path,
  () => {
    getBreadcrumbs()
  },
  { immediate: true }
)

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const handleExport = () => {
  ElMessage.success('已生成当前视图导出任务')
}

const handleCommand = async (command: string) => {
  if (command !== 'logout') return

  ElMessageBox.confirm('确定要退出登录吗？', '退出确认', {
    confirmButtonText: '退出',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      await authStore.logout()
    })
    .catch(() => {
      // 用户取消
    })
}
</script>

<style scoped lang="scss">
.layout-shell {
  display: grid;
  grid-template-columns: 236px minmax(0, 1fr);
  min-height: 100vh;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.76), rgba(245, 241, 234, 0.94)),
    var(--color-bg-secondary);
  color: var(--color-text-primary);
  overflow: hidden;

  &.is-collapsed {
    grid-template-columns: 72px minmax(0, 1fr);
  }
}

.layout-aside {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background:
    radial-gradient(circle at 20% 0%, rgba(209, 154, 54, 0.14), transparent 28%),
    linear-gradient(180deg, #071114 0%, #0D181B 48%, #081113 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 12px 0 32px rgba(7, 17, 20, 0.18);
  transition: width $duration-base $easing-ease-in-out;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  min-height: 64px;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  border-radius: 10px;
  color: #F5D28F;
  background: rgba(245, 210, 143, 0.1);
  box-shadow: inset 0 0 0 1px rgba(245, 210, 143, 0.22);

  .el-icon {
    font-size: 24px;
  }
}

.brand-copy {
  min-width: 0;
  display: grid;
  gap: 2px;
}

.brand-title {
  color: #F6D794;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.1;
  white-space: nowrap;
}

.brand-subtitle {
  color: rgba(255, 255, 255, 0.48);
  font-size: 11px;
    letter-spacing: 0;
  text-transform: uppercase;
}

:deep(.sidebar-menu) {
  --el-menu-bg-color: transparent;
  --el-menu-text-color: rgba(255, 255, 255, 0.68);
  --el-menu-active-color: #fff;
  flex: 1;
  border-right: 0;
  padding: 10px 8px;
  background: transparent !important;
  overflow-y: auto;
  overflow-x: hidden;

  .el-menu-item,
  .el-sub-menu__title {
    height: 42px;
    margin: 4px 0;
    padding: 0 12px !important;
    border-radius: 6px;
    color: rgba(255, 255, 255, 0.68) !important;
    font-weight: 600;
    letter-spacing: 0;
    transition: background 0.18s ease, color 0.18s ease;

    .el-icon {
      margin-right: 12px;
      color: rgba(255, 255, 255, 0.58);
    }

    &:hover {
      background: rgba(255, 255, 255, 0.06) !important;
      color: #fff !important;

      .el-icon {
        color: #F5D28F;
      }
    }

    &.is-active {
      background: linear-gradient(180deg, #D52A2A, #B71920) !important;
      color: #fff !important;
      box-shadow: 0 10px 22px rgba(200, 30, 30, 0.28);

      .el-icon {
        color: #fff;
      }
    }
  }

  .el-sub-menu {
    .el-menu {
      background: transparent !important;
      padding-left: 8px;
    }

    &.is-opened > .el-sub-menu__title {
      color: #fff !important;
    }
  }
}

.collapse-dock {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 52px;
  padding: 0 18px;
  border: 0;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  color: rgba(255, 255, 255, 0.7);
  font: inherit;
  cursor: pointer;
  text-align: left;

  &:hover {
    color: #F5D28F;
    background: rgba(255, 255, 255, 0.05);
  }
}

.layout-workspace {
  min-width: 0;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  min-height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 0 24px;
  background: rgba(255, 253, 249, 0.86);
  border-bottom: 1px solid rgba(65, 54, 42, 0.1);
  backdrop-filter: blur(10px);
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
  min-width: 0;
}

.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #28211A;
  font-size: 15px;
  font-weight: 800;
  min-width: 0;
}

.breadcrumb-separator,
.header-context {
  color: #8A8074;
  font-size: 13px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.header-date {
  width: 248px;
}

.header-select {
  width: 148px;
}

.header-icon-btn {
  border-color: #D7CEC2;
  background: #FFFDF9;
  color: #332D28;
  font-weight: 700;
}

.header-round-btn {
  border-color: #D7CEC2;
  background: #FFFDF9;
  color: #695F55;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  height: 42px;
  padding: 4px 8px 4px 4px;
  border: 0;
  background: transparent;
  color: #332D28;
  cursor: pointer;
}

.user-meta {
  display: grid;
  text-align: left;
  line-height: 1.1;

  strong {
    font-size: 14px;
    font-weight: 800;
  }

  small {
    margin-top: 3px;
    color: #8A8074;
    font-size: 12px;
  }
}

.layout-main {
  flex: 1;
  min-height: 0;
  padding: 24px;
  overflow-y: auto;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: opacity 0.16s ease, transform 0.16s ease;
}

.fade-transform-enter-from,
.fade-transform-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (max-width: 1180px) {
  .layout-shell {
    grid-template-columns: 72px minmax(0, 1fr);
  }

  .brand-copy,
  .collapse-dock span {
    display: none;
  }

  .header-date {
    width: 220px;
  }
}

@media (max-width: 860px) {
  .layout-shell {
    display: block;
  }

  .layout-aside {
    position: fixed;
    inset: 0 auto 0 0;
    width: 72px;
    z-index: 30;
  }

  .layout-workspace {
    margin-left: 72px;
  }

  .layout-header {
    align-items: flex-start;
    flex-direction: column;
    height: auto;
    padding: 14px 16px;
  }

  .header-actions {
    width: 100%;
    overflow-x: auto;
    padding-bottom: 2px;
  }

  .layout-main {
    padding: 16px;
  }
}
</style>
