<template>
  <div class="roles-container">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="角色管理" name="roles">
        <div class="action-bar">
          <div class="left-actions">
            <el-button
              v-permission="PERMISSIONS.ROLE_CREATE"
              type="primary"
              @click="handleCreate"
            >
              <el-icon><Plus /></el-icon>
              新增角色
            </el-button>
          </div>

          <div class="right-actions">
            <el-input
              v-model="roleFilterForm.search"
              placeholder="搜索角色名称或编码"
              clearable
              style="width: 300px"
              @clear="loadRoleData"
            >
              <template #append>
                <el-button :icon="Search" @click="loadRoleData" />
              </template>
            </el-input>

            <el-select
              v-model="roleFilterForm.is_active"
              placeholder="状态"
              clearable
              style="width: 120px; margin-left: 12px"
              @change="loadRoleData"
            >
              <el-option label="启用" :value="true" />
              <el-option label="禁用" :value="false" />
            </el-select>
          </div>
        </div>

        <el-table
          v-loading="roleLoading"
          :data="roleTableData"
          border
          stripe
          style="width: 100%"
        >
          <el-table-column prop="code" label="角色编码" width="150" />
          <el-table-column prop="name" label="角色名称" width="150" />
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />

          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="权限数" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="info">{{ row.permission_count }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column label="用户数" width="100" align="center">
            <template #default="{ row }">
              <el-tag type="info">{{ row.user_count }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="260" fixed="right">
            <template #default="{ row }">
              <el-button
                v-permission="PERMISSIONS.ROLE_ASSIGN_PERMISSION"
                type="primary"
                size="small"
                link
                @click="handleAssignPermissions(row)"
              >
                分配权限
              </el-button>

              <el-button
                v-permission="PERMISSIONS.ROLE_EDIT"
                type="primary"
                size="small"
                link
                @click="handleEdit(row)"
              >
                编辑
              </el-button>

              <el-popconfirm
                title="确定要删除这个角色吗？"
                @confirm="handleDelete(row)"
              >
                <template #reference>
                  <el-button
                    v-permission="PERMISSIONS.ROLE_DELETE"
                    type="danger"
                    size="small"
                    link
                  >
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination">
          <el-pagination
            v-model:current-page="rolePagination.page"
            v-model:page-size="rolePagination.pageSize"
            :total="rolePagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadRoleData"
            @current-change="loadRoleData"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane label="用户管理" name="users">
        <div class="action-bar">
          <div class="left-actions">
            <el-button
              v-permission="[PERMISSIONS.USER_CREATE, PERMISSIONS.ROLE_EDIT]"
              type="primary"
              @click="handleCreateUser"
            >
              <el-icon><Plus /></el-icon>
              新增用户
            </el-button>
          </div>
          <div class="right-actions">
            <el-input
              v-model="userFilterForm.search"
              placeholder="搜索用户名/姓名/手机号"
              clearable
              style="width: 300px"
              @clear="loadUserData"
            >
              <template #append>
                <el-button :icon="Search" @click="loadUserData" />
              </template>
            </el-input>

            <el-select
              v-model="userFilterForm.is_active"
              placeholder="状态"
              clearable
              style="width: 120px; margin-left: 12px"
              @change="loadUserData"
            >
              <el-option label="启用" :value="true" />
              <el-option label="禁用" :value="false" />
            </el-select>
          </div>
        </div>

        <el-table
          v-loading="userLoading"
          :data="userTableData"
          border
          stripe
          style="width: 100%"
        >
          <el-table-column prop="username" label="用户名" width="140" />
          <el-table-column prop="full_name" label="姓名" width="140">
            <template #default="{ row }">
              {{ row.full_name || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="phone" label="手机号" width="140">
            <template #default="{ row }">
              {{ row.phone || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="email" label="邮箱" min-width="220" show-overflow-tooltip />

          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'danger'">
                {{ row.is_active ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="当前角色" min-width="220">
            <template #default="{ row }">
              <el-space wrap>
                <el-tag v-for="role in row.roles" :key="role.id" type="info">
                  {{ role.name }}
                </el-tag>
                <span v-if="!row.roles || row.roles.length === 0">-</span>
              </el-space>
            </template>
          </el-table-column>

          <el-table-column prop="updated_at" label="更新时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.updated_at) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="220" fixed="right">
            <template #default="{ row }">
              <el-button
                v-permission="[PERMISSIONS.USER_EDIT, PERMISSIONS.ROLE_EDIT]"
                type="primary"
                size="small"
                link
                @click="handleEditUser(row)"
              >
                编辑
              </el-button>

              <el-popconfirm
                :title="`确定要${row.is_active ? '禁用' : '启用'}该用户吗？`"
                @confirm="handleToggleUserStatus(row)"
              >
                <template #reference>
                  <el-button
                    v-permission="[PERMISSIONS.USER_EDIT, PERMISSIONS.ROLE_EDIT]"
                    :type="row.is_active ? 'danger' : 'success'"
                    size="small"
                    link
                  >
                    {{ row.is_active ? '禁用' : '启用' }}
                  </el-button>
                </template>
              </el-popconfirm>

              <el-button
                v-permission="PERMISSIONS.ROLE_ASSIGN_USER"
                type="primary"
                size="small"
                link
                @click="handleAssignUserRoles(row)"
              >
                分配角色
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination">
          <el-pagination
            v-model:current-page="userPagination.page"
            v-model:page-size="userPagination.pageSize"
            :total="userPagination.total"
            :page-sizes="[10, 20, 50, 100]"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadUserData"
            @current-change="loadUserData"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <EditRoleDialog
      v-model:visible="editDialogVisible"
      :role-data="currentRole"
      :permissions="allPermissions"
      @success="handleRoleDialogSuccess"
    />

    <AssignPermissionsDialog
      v-model:visible="assignDialogVisible"
      :role="currentRole"
      :permissions="allPermissions"
      @success="handleRoleDialogSuccess"
    />

    <AssignUserRolesDialog
      v-model:visible="assignUserRoleDialogVisible"
      :user="currentUser"
      :roles="roleOptions"
      @success="handleUserRoleDialogSuccess"
    />

    <EditUserDialog
      v-model:visible="editUserDialogVisible"
      :user-data="currentEditableUser"
      @success="handleUserDialogSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { roleApi, permissionApi } from '@/api'
import type { RoleListItem, Role, UserRoleListItem, UserWithRoles } from '@/api/role'
import type { Permission } from '@/api/permission'
import EditRoleDialog from '@/components/dialogs/EditRoleDialog.vue'
import AssignPermissionsDialog from '@/components/dialogs/AssignPermissionsDialog.vue'
import AssignUserRolesDialog from '@/components/dialogs/AssignUserRolesDialog.vue'
import EditUserDialog from '@/components/dialogs/EditUserDialog.vue'
import { PERMISSIONS } from '@/config'

const activeTab = ref('roles')

const roleLoading = ref(false)
const roleTableData = ref<RoleListItem[]>([])
const roleOptions = ref<RoleListItem[]>([])

const rolePagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const roleFilterForm = reactive({
  search: '',
  is_active: undefined as boolean | undefined
})

const userLoading = ref(false)
const userTableData = ref<UserRoleListItem[]>([])

const userPagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const userFilterForm = reactive({
  search: '',
  is_active: undefined as boolean | undefined
})

const editDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const currentRole = ref<Role | undefined>()

const assignUserRoleDialogVisible = ref(false)
const currentUser = ref<UserWithRoles | undefined>()
const editUserDialogVisible = ref(false)
const currentEditableUser = ref<UserRoleListItem | undefined>()

const allPermissions = ref<Permission[]>([])

const unwrapData = <T>(response: unknown): T => {
  const value = response as { data?: { data?: T } | T }
  if (value?.data && typeof value.data === 'object' && 'data' in (value.data as Record<string, unknown>)) {
    return (value.data as { data: T }).data
  }
  return (value?.data as T) ?? (response as T)
}

const unwrapTotal = (response: unknown): number => {
  const value = response as { total?: number; data?: { total?: number } }
  return value?.total ?? value?.data?.total ?? 0
}

const loadRoleData = async () => {
  roleLoading.value = true
  try {
    const res = await roleApi.roleApi.getList({
      page: rolePagination.page,
      page_size: rolePagination.pageSize,
      search: roleFilterForm.search || undefined,
      is_active: roleFilterForm.is_active
    })

    roleTableData.value = unwrapData<RoleListItem[]>(res) || []
    rolePagination.total = unwrapTotal(res)
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '加载失败'
    ElMessage.error(message)
  } finally {
    roleLoading.value = false
  }
}

const loadRoleOptions = async () => {
  try {
    const res = await roleApi.roleApi.getList({ page: 1, page_size: 100 })
    roleOptions.value = unwrapData<RoleListItem[]>(res) || []
  } catch {
    ElMessage.error('加载角色选项失败')
  }
}

const loadAllPermissions = async () => {
  try {
    const res = await permissionApi.permissionApi.getAll()
    allPermissions.value = unwrapData<Permission[]>(res) || []
  } catch {
    ElMessage.error('加载权限列表失败')
  }
}

const loadUserData = async () => {
  userLoading.value = true
  try {
    const res = await roleApi.roleApi.getUserList({
      page: userPagination.page,
      page_size: userPagination.pageSize,
      search: userFilterForm.search || undefined,
      is_active: userFilterForm.is_active
    })

    userTableData.value = unwrapData<UserRoleListItem[]>(res) || []
    userPagination.total = unwrapTotal(res)
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '加载用户失败'
    ElMessage.error(message)
  } finally {
    userLoading.value = false
  }
}

const handleCreate = () => {
  currentRole.value = undefined
  editDialogVisible.value = true
}

const handleEdit = async (row: RoleListItem) => {
  try {
    const res = await roleApi.roleApi.getDetail(row.id)
    currentRole.value = unwrapData<Role>(res)
    editDialogVisible.value = true
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '获取角色详情失败'
    ElMessage.error(message)
  }
}

const handleAssignPermissions = async (row: RoleListItem) => {
  try {
    const res = await roleApi.roleApi.getDetail(row.id)
    currentRole.value = unwrapData<Role>(res)
    assignDialogVisible.value = true
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '获取角色详情失败'
    ElMessage.error(message)
  }
}

const handleDelete = async (row: RoleListItem) => {
  try {
    await roleApi.roleApi.delete(row.id)
    ElMessage.success('删除成功')
    await Promise.all([loadRoleData(), loadRoleOptions(), loadUserData()])
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '删除失败'
    ElMessage.error(message)
  }
}

const handleAssignUserRoles = async (row: UserRoleListItem) => {
  try {
    const res = await roleApi.roleApi.getUserRoles(row.id)
    currentUser.value = unwrapData<UserWithRoles>(res)
    assignUserRoleDialogVisible.value = true
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '获取用户角色失败'
    ElMessage.error(message)
  }
}

const handleCreateUser = () => {
  currentEditableUser.value = undefined
  editUserDialogVisible.value = true
}

const handleEditUser = (row: UserRoleListItem) => {
  currentEditableUser.value = row
  editUserDialogVisible.value = true
}

const handleToggleUserStatus = async (row: UserRoleListItem) => {
  try {
    await roleApi.roleApi.updateUserStatus(row.id, { is_active: !row.is_active })
    ElMessage.success(`用户已${row.is_active ? '禁用' : '启用'}`)
    await loadUserData()
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '更新用户状态失败'
    ElMessage.error(message)
  }
}

const handleRoleDialogSuccess = async () => {
  await Promise.all([loadRoleData(), loadRoleOptions(), loadUserData()])
}

const handleUserRoleDialogSuccess = async () => {
  await Promise.all([loadRoleData(), loadUserData()])
}

const handleUserDialogSuccess = async () => {
  await loadUserData()
}

const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadRoleData()
  loadRoleOptions()
  loadAllPermissions()
  loadUserData()
})
</script>

<style scoped>
.roles-container {
  padding: 20px;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.left-actions {
  display: flex;
  gap: 12px;
}

.right-actions {
  display: flex;
  align-items: center;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
