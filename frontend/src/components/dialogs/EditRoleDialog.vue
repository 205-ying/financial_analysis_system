<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑角色' : '新增角色'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="角色编码" prop="code">
        <el-input
          v-model="formData.code"
          :disabled="isEdit"
          placeholder="请输入角色编码，如：manager"
        />
      </el-form-item>

      <el-form-item label="角色名称" prop="name">
        <el-input v-model="formData.name" placeholder="请输入角色名称" />
      </el-form-item>

      <el-form-item label="角色描述" prop="description">
        <el-input
          v-model="formData.description"
          type="textarea"
          :rows="3"
          placeholder="请输入角色描述"
        />
      </el-form-item>

      <el-form-item label="是否启用" prop="is_active">
        <el-switch v-model="formData.is_active" />
      </el-form-item>

      <el-form-item v-if="!isEdit" label="分配权限" prop="permission_ids">
        <el-tree
          ref="treeRef"
          :data="permissionTree"
          show-checkbox
          node-key="id"
          :props="{ children: 'children', label: 'name' }"
          :default-checked-keys="formData.permission_ids"
          @check="handleCheckChange"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { roleApi } from '@/api'
import type { RoleCreateParams, RoleUpdateParams } from '@/api/role'
import type { Permission } from '@/api/permission'

interface Props {
  visible: boolean
  roleData?: any
  permissions?: Permission[]
}

interface Emits {
  (e: 'update:visible', visible: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const treeRef = ref()
const loading = ref(false)

const isEdit = computed(() => !!props.roleData)

const formData = reactive<RoleCreateParams & { permission_ids: number[] }>({
  code: '',
  name: '',
  description: '',
  is_active: true,
  permission_ids: []
})

const rules: FormRules = {
  code: [
    { required: true, message: '请输入角色编码', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ]
}

// 权限树结构
const permissionTree = computed(() => {
  if (!props.permissions) return []
  
  // 按资源分组
  const grouped = props.permissions.reduce((acc, perm) => {
    if (!acc[perm.resource]) {
      acc[perm.resource] = []
    }
    acc[perm.resource].push(perm)
    return acc
  }, {} as Record<string, Permission[]>)

  // 转换为树结构
  return Object.entries(grouped).map(([resource, perms]) => ({
    id: `resource_${resource}`,
    name: resource,
    children: perms.map(p => ({
      id: p.id,
      name: `${p.name} (${p.action})`
    }))
  }))
})

watch(
  () => props.visible,
  (val) => {
    if (val && props.roleData) {
      // 编辑模式
      Object.assign(formData, {
        name: props.roleData.name,
        description: props.roleData.description,
        is_active: props.roleData.is_active
      })
    } else if (val) {
      // 新增模式，重置表单
      formRef.value?.resetFields()
      formData.code = ''
      formData.name = ''
      formData.description = ''
      formData.is_active = true
      formData.permission_ids = []
    }
  }
)

const handleCheckChange = () => {
  // 获取选中的叶子节点（实际权限ID）
  const checkedKeys = treeRef.value.getCheckedKeys()
  formData.permission_ids = checkedKeys.filter((key: any) => typeof key === 'number')
}

const handleClose = () => {
  emit('update:visible', false)
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      if (isEdit.value) {
        // 更新角色
        const updateData: RoleUpdateParams = {
          name: formData.name,
          description: formData.description,
          is_active: formData.is_active
        }
        await roleApi.roleApi.update(props.roleData.id, updateData)
        ElMessage.success('更新成功')
      } else {
        // 创建角色
        await roleApi.roleApi.create(formData)
        ElMessage.success('创建成功')
      }
      
      emit('success')
      handleClose()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      loading.value = false
    }
  })
}
</script>
