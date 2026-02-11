<template>
  <el-dialog
    :model-value="visible"
    title="分配权限"
    width="700px"
    @close="handleClose"
  >
    <div style="margin-bottom: 16px">
      <el-input
        v-model="searchText"
        placeholder="搜索权限"
        clearable
        style="width: 300px"
      />
    </div>

    <el-tree
      ref="treeRef"
      :data="permissionTree"
      show-checkbox
      default-expand-all
      node-key="id"
      :props="{ children: 'children', label: 'name' }"
      :filter-node-method="filterNode"
      @check="handleCheckChange"
    >
      <template #default="{ data }">
        <span class="tree-node-label">
          <span>{{ data.name }}</span>
          <span v-if="data.description" class="node-description">
            ({{ data.description }})
          </span>
        </span>
      </template>
    </el-tree>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { roleApi } from '@/api'
import type { Permission } from '@/api/permission'
import type { Role } from '@/api/role'

interface Props {
  visible: boolean
  role?: Role
  permissions?: Permission[]
}

interface Emits {
  (e: 'update:visible', visible: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const treeRef = ref()
const loading = ref(false)
const searchText = ref('')
const selectedPermissionIds = ref<number[]>([])

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
    isResource: true,
    children: perms.map(p => ({
      id: p.id,
      name: `${p.name} (${p.action})`,
      description: p.description,
      isResource: false
    }))
  }))
})

// 过滤后的树
const filteredPermissionTree = computed(() => {
  if (!searchText.value) return permissionTree.value
  
  return permissionTree.value.map(resource => ({
    ...resource,
    children: resource.children.filter(perm =>
      perm.name.toLowerCase().includes(searchText.value.toLowerCase())
    )
  })).filter(resource => resource.children.length > 0)
})

// 树节点过滤方法
const filterNode = (value: string, data: any) => {
  if (!value) return true
  return data.name.toLowerCase().includes(value.toLowerCase())
}

// 监听搜索框变化，触发树的过滤
watch(searchText, (val) => {
  if (treeRef.value) {
    treeRef.value.filter(val)
  }
})

watch(
  () => props.visible,
  async (val) => {
    if (val && props.role) {
      // 重置搜索框，确保显示完整树结构
      searchText.value = ''
      
      // 多次 nextTick 确保 DOM 完全更新
      await nextTick()
      await nextTick()
      
      if (treeRef.value && props.permissions && props.permissions.length > 0) {
        // 先清空所有选中状态
        treeRef.value.setCheckedKeys([])
        
        // 等待清空操作完成
        await nextTick()
        
        // 设置当前角色已有的权限为选中状态
        const rolePermissionIds = props.role.permissions?.map(p => p.id) || []
        console.log('初始化角色权限:', rolePermissionIds)
        console.log('可用权限总数:', props.permissions.length)
        
        if (rolePermissionIds.length > 0) {
          treeRef.value.setCheckedKeys(rolePermissionIds, true)
        }
        
        // 验证设置是否成功
        await nextTick()
        const actualChecked = treeRef.value.getCheckedKeys(true)
        console.log('实际选中的权限:', actualChecked)
        
        // 初始化 selectedPermissionIds 为当前选中的实际值
        selectedPermissionIds.value = [...actualChecked.filter((key: any) => typeof key === 'number')]
      }
    }
  },
  { flush: 'post' }
)

const handleCheckChange = () => {
  if (!treeRef.value) return
  
  // 获取所有选中的叶子节点（实际权限ID）
  // 参数 true 表示只返回叶子节点，不包括父节点
  const checkedKeys = treeRef.value.getCheckedKeys(true)
  
  // 只保留数字类型的ID（实际权限ID，过滤掉字符串类型的资源分组ID）
  selectedPermissionIds.value = checkedKeys.filter((key: any) => typeof key === 'number')
  
  console.log('权限发生变化:', selectedPermissionIds.value)
}

const handleClose = () => {
  emit('update:visible', false)
  // 延迟重置，避免关闭动画期间看到状态变化
  setTimeout(() => {
    searchText.value = ''
    selectedPermissionIds.value = []
    if (treeRef.value) {
      treeRef.value.setCheckedKeys([])
    }
  }, 300)
}

const handleSubmit = async () => {
  if (!props.role || !treeRef.value) return

  loading.value = true
  try {
    // 从树组件直接获取当前所有选中的叶子节点权限ID
    // 参数 true 表示只返回叶子节点（实际权限），不包括父节点（资源分组）
    const checkedKeys = treeRef.value.getCheckedKeys(true)
    const permissionIds = checkedKeys.filter((key: any) => typeof key === 'number')
    
    console.log('=== 提交权限 ===')
    console.log('树返回的选中节点:', checkedKeys)
    console.log('过滤后的权限ID:', permissionIds)
    console.log('角色原有权限:', props.role.permissions?.map(p => p.id))
    
    await roleApi.roleApi.assignPermissions(props.role.id, {
      permission_ids: permissionIds
    })
    
    ElMessage.success('分配权限成功')
    emit('success')
    handleClose()
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tree-node-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-description {
  color: #909399;
  font-size: 12px;
}
</style>
