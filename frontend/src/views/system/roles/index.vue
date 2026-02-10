<template>
  <div class="roles-container">
    <!-- 顶部操作栏 -->
    <div class="action-bar">
      <div class="left-actions">
        <el-button
          v-permission="'role:create'"
          type="primary"
          @click="handleCreate"
        >
          <el-icon><Plus /></el-icon>
          新增角色
        </el-button>
      </div>

      <div class="right-actions">
        <el-input
          v-model="filterForm.search"
          placeholder="搜索角色名称或编码"
          clearable
          style="width: 300px"
          @clear="loadData"
        >
          <template #append>
            <el-button :icon="Search" @click="loadData" />
          </template>
        </el-input>

        <el-select
          v-model="filterForm.is_active"
          placeholder="状态"
          clearable
          style="width: 120px; margin-left: 12px"
          @change="loadData"
        >
          <el-option label="启用" :value="true" />
          <el-option label="禁用" :value="false" />
        </el-select>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table
      v-loading="loading"
      :data="tableData"
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
            v-permission="'role:assign-permission'"
            type="primary"
            size="small"
            link
            @click="handleAssignPermissions(row)"
          >
            分配权限
          </el-button>
          
          <el-button
            v-permission="'role:edit'"
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
                v-permission="'role:delete'"
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

    <!-- 分页 -->
    <div class="pagination">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 编辑角色对话框 -->
    <EditRoleDialog
      v-model:visible="editDialogVisible"
      :role-data="currentRole"
      :permissions="allPermissions"
      @success="loadData"
    />

    <!-- 分配权限对话框 -->
    <AssignPermissionsDialog
      v-model:visible="assignDialogVisible"
      :role="currentRole"
      :permissions="allPermissions"
      @success="loadData"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { roleApi, permissionApi } from '@/api'
import type { RoleListItem, Role } from '@/api/role'
import type { Permission } from '@/api/permission'
import EditRoleDialog from '@/components/dialogs/EditRoleDialog.vue'
import AssignPermissionsDialog from '@/components/dialogs/AssignPermissionsDialog.vue'

// 表格数据
const loading = ref(false)
const tableData = ref<RoleListItem[]>([])

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

// 筛选表单
const filterForm = reactive({
  search: '',
  is_active: undefined as boolean | undefined
})

// 对话框
const editDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const currentRole = ref<Role | undefined>()

// 所有权限列表
const allPermissions = ref<Permission[]>([])

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await roleApi.roleApi.getList({
      page: pagination.page,
      page_size: pagination.pageSize,
      search: filterForm.search || undefined,
      is_active: filterForm.is_active
    })

    tableData.value = res.data
    pagination.total = res.total
  } catch (error: any) {
    ElMessage.error(error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 加载所有权限
const loadAllPermissions = async () => {
  try {
    const res = await permissionApi.permissionApi.getAll()
    allPermissions.value = res.data
  } catch (error: any) {
    ElMessage.error('加载权限列表失败')
  }
}

// 新增角色
const handleCreate = () => {
  currentRole.value = undefined
  editDialogVisible.value = true
}

// 编辑角色
const handleEdit = async (row: RoleListItem) => {
  try {
    const res = await roleApi.roleApi.getDetail(row.id)
    currentRole.value = res.data
    editDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取角色详情失败')
  }
}

// 分配权限
const handleAssignPermissions = async (row: RoleListItem) => {
  try {
    const res = await roleApi.roleApi.getDetail(row.id)
    currentRole.value = res.data
    assignDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取角色详情失败')
  }
}

// 删除角色
const handleDelete = async (row: RoleListItem) => {
  try {
    await roleApi.roleApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error: any) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 格式化日期时间
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

// 初始化
onMounted(() => {
  loadData()
  loadAllPermissions()
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
