<template>
  <el-dialog
    v-model="visible"
    title="新增费用"
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

      <el-form-item label="费用类型" prop="expense_type_id">
        <el-select
          v-model="form.expense_type_id"
          placeholder="请选择费用类型"
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="type in expenseTypeList"
            :key="type.id"
            :label="type.name"
            :value="type.id"
          >
            <span>{{ type.name }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">
              {{ type.category }}
            </span>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="费用日期" prop="biz_date">
        <el-date-picker
          v-model="form.biz_date"
          type="date"
          placeholder="请选择费用日期"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="费用金额" prop="amount">
        <el-input-number
          v-model="form.amount"
          :precision="2"
          :min="0"
          :max="999999"
          :controls="false"
          style="width: 100%"
          placeholder="请输入费用金额"
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
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { createExpenseRecord, getExpenseTypeList } from '@/api/expense'
import StoreSelect from '@/components/StoreSelect.vue'
import type { ExpenseRecordCreate, ExpenseTypeInfo } from '@/types'

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
const expenseTypeList = ref<ExpenseTypeInfo[]>([])

const form = reactive<ExpenseRecordCreate>({
  store_id: undefined as any,
  expense_type_id: undefined as any,
  biz_date: '',
  amount: 0,
  remark: ''
})

const rules: FormRules = {
  store_id: [{ required: true, message: '请选择门店', trigger: 'change' }],
  expense_type_id: [{ required: true, message: '请选择费用类型', trigger: 'change' }],
  biz_date: [{ required: true, message: '请选择费用日期', trigger: 'change' }],
  amount: [
    { required: true, message: '请输入费用金额', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '费用金额必须大于 0', trigger: 'blur' }
  ]
}

// 加载费用类型列表
const loadExpenseTypes = async () => {
  try {
    const { data } = await getExpenseTypeList()
    expenseTypeList.value = data
  } catch (error) {
    console.error('加载费用类型失败:', error)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    loading.value = true

    await createExpenseRecord(form)
    ElMessage.success('费用创建成功')
    emit('success')
    handleCancel()
  } catch (error: any) {
    if (error !== false) {
      console.error('创建费用失败:', error)
      ElMessage.error(error.response?.data?.message || '创建费用失败')
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
  // 打开对话框时设置默认日期为今天
  if (val && !form.biz_date) {
    const today = new Date()
    form.biz_date = today.toISOString().slice(0, 10)
  }
  // 加载费用类型列表（只在首次打开时加载）
  if (val && expenseTypeList.value.length === 0) {
    loadExpenseTypes()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})
</script>
