<template>
  <el-dialog
    v-model="visible"
    title="新增订单"
    width="600px"
    :close-on-click-modal="false"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="门店" prop="store_id">
        <StoreSelect v-model="form.store_id" width="100%" />
      </el-form-item>

      <el-form-item label="订单号" prop="order_no">
        <el-input
          v-model="form.order_no"
          placeholder="请输入订单号"
          clearable
        />
      </el-form-item>

      <el-form-item label="渠道" prop="channel">
        <el-select
          v-model="form.channel"
          placeholder="请选择渠道"
          style="width: 100%"
        >
          <el-option label="堂食" value="堂食" />
          <el-option label="外卖" value="外卖" />
          <el-option label="外带" value="外带" />
          <el-option label="团购" value="团购" />
        </el-select>
      </el-form-item>

      <el-form-item label="订单金额" prop="net_amount">
        <el-input-number
          v-model="form.net_amount"
          :precision="2"
          :min="0"
          :max="999999"
          :controls="false"
          style="width: 100%"
          placeholder="请输入订单金额"
        />
      </el-form-item>

      <el-form-item label="订单时间" prop="order_time">
        <el-date-picker
          v-model="form.order_time"
          type="datetime"
          placeholder="请选择订单时间"
          value-format="YYYY-MM-DD HH:mm:ss"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="备注" prop="remark">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="3"
          placeholder="请输入备注信息（可选）"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { createOrder } from '@/api/order'
import StoreSelect from '@/components/StoreSelect.vue'
import type { OrderCreate } from '@/types'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'success': []
}>()

const visible = ref(props.modelValue)
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = reactive<Partial<OrderCreate>>({
  store_id: undefined,
  channel: '',
  order_no: '',
  net_amount: 0,
  order_time: '',
  remark: ''
})

const rules: FormRules = {
  store_id: [{ required: true, message: '请选择门店', trigger: 'change' }],
  order_no: [
    { required: true, message: '请输入订单号', trigger: 'blur' },
    { min: 3, max: 50, message: '订单号长度在 3 到 50 个字符', trigger: 'blur' }
  ],
  channel: [{ required: true, message: '请选择渠道', trigger: 'change' }],
  net_amount: [
    { required: true, message: '请输入订单金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '订单金额必须大于 0', trigger: 'blur' }
  ],
  order_time: [{ required: true, message: '请选择订单时间', trigger: 'change' }]
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    const payload: OrderCreate = {
      store_id: form.store_id!,
      channel: form.channel!,
      order_no: form.order_no!,
      net_amount: form.net_amount ?? 0,
      order_time: form.order_time!,
      remark: form.remark ?? ''
    }

    await createOrder(payload)
    ElMessage.success('订单创建成功')
    emit('success')
    handleCancel()
  } catch (error: unknown) {
    if (error !== false) {
      const message = error instanceof Error ? error.message : '创建订单失败'
      ElMessage.error(message)
    }
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  emit('update:modelValue', false)
}

const handleClosed = () => {
  formRef.value?.resetFields()
  form.remark = ''
}

// 监听 modelValue 变化
import { watch } from 'vue'
watch(() => props.modelValue, (val) => {
  visible.value = val
  // 打开对话框时设置默认订单时间为当前时间
  if (val && !form.order_time) {
    const now = new Date()
    form.order_time = now.toISOString().slice(0, 19).replace('T', ' ')
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})
</script>
