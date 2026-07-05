<template>
  <el-dialog
    :model-value="visible"
    title="分配角色"
    width="520px"
    @close="handleClose"
  >
    <div v-if="user" class="user-summary">
      <div><span class="label">用户名：</span>{{ user.username }}</div>
      <div><span class="label">姓名：</span>{{ user.full_name || '-' }}</div>
    </div>

    <el-form label-width="90px">
      <el-form-item label="角色选择">
        <el-select
          v-model="selectedRoleIds"
          multiple
          filterable
          collapse-tags
          collapse-tags-tooltip
          placeholder="请选择角色"
          style="width: 100%"
        >
          <el-option
            v-for="role in roles"
            :key="role.id"
            :label="`${role.name} (${role.code})`"
            :value="role.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        保存
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { roleApi } from '@/api'
import type { RoleListItem, UserWithRoles } from '@/api/role'

interface Props {
  visible: boolean
  user?: UserWithRoles
  roles: RoleListItem[]
}

interface Emits {
  (e: 'update:visible', visible: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const loading = ref(false)
const selectedRoleIds = ref<number[]>([])

watch(
  () => props.visible,
  (visible) => {
    if (visible && props.user) {
      selectedRoleIds.value = props.user.roles.map(item => item.id)
    }
  }
)

const handleClose = () => {
  emit('update:visible', false)
}

const handleSubmit = async () => {
  if (!props.user) return

  loading.value = true
  try {
    await roleApi.roleApi.assignUserRoles(props.user.id, {
      role_ids: selectedRoleIds.value
    })
    ElMessage.success('分配角色成功')
    emit('success')
    handleClose()
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : '分配角色失败'
    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.user-summary {
  margin-bottom: 14px;
  color: #606266;
  line-height: 24px;
}

.label {
  color: #909399;
}
</style>
