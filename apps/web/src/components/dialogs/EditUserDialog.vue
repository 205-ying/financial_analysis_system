<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑用户' : '新增用户'"
    width="560px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="用户名" prop="username">
        <el-input
          v-model="formData.username"
          :disabled="isEdit"
          placeholder="请输入用户名"
        />
      </el-form-item>

      <el-form-item v-if="!isEdit" label="登录密码" prop="password">
        <el-input
          v-model="formData.password"
          type="password"
          show-password
          placeholder="请输入登录密码"
        />
      </el-form-item>

      <el-form-item label="邮箱" prop="email">
        <el-input v-model="formData.email" placeholder="请输入邮箱" />
      </el-form-item>

      <el-form-item label="姓名" prop="full_name">
        <el-input v-model="formData.full_name" placeholder="请输入姓名（可选）" />
      </el-form-item>

      <el-form-item label="手机号" prop="phone">
        <el-input v-model="formData.phone" placeholder="请输入手机号（可选）" />
      </el-form-item>

      <el-form-item v-if="!isEdit" label="是否启用" prop="is_active">
        <el-switch v-model="formData.is_active" />
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
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { roleApi } from '@/api'
import type { UserCreateParams, UserUpdateParams, UserRoleListItem } from '@/api/role'

interface Props {
  visible: boolean
  userData?: UserRoleListItem
}

interface Emits {
  (e: 'update:visible', visible: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const loading = ref(false)

const isEdit = computed(() => !!props.userData)

const formData = reactive<UserCreateParams>({
  username: '',
  email: '',
  password: '',
  full_name: '',
  phone: '',
  is_active: true
})

const rules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 64, message: '长度在 6 到 64 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ]
}

watch(
  () => props.visible,
  (val) => {
    if (!val) return

    if (props.userData) {
      formData.username = props.userData.username
      formData.email = props.userData.email
      formData.password = ''
      formData.full_name = props.userData.full_name || ''
      formData.phone = props.userData.phone || ''
      formData.is_active = props.userData.is_active
    } else {
      formRef.value?.resetFields()
      formData.username = ''
      formData.email = ''
      formData.password = ''
      formData.full_name = ''
      formData.phone = ''
      formData.is_active = true
    }
  }
)

const handleClose = () => {
  emit('update:visible', false)
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      if (isEdit.value && props.userData) {
        const updateData: UserUpdateParams = {
          email: formData.email,
          full_name: formData.full_name || undefined,
          phone: formData.phone || undefined
        }
        await roleApi.roleApi.updateUser(props.userData.id, updateData)
        ElMessage.success('用户更新成功')
      } else {
        await roleApi.roleApi.createUser({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          full_name: formData.full_name || undefined,
          phone: formData.phone || undefined,
          is_active: formData.is_active
        })
        ElMessage.success('用户创建成功')
      }

      emit('success')
      handleClose()
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : '操作失败'
      ElMessage.error(message)
    } finally {
      loading.value = false
    }
  })
}
</script>
