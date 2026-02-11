<template>
  <div class="budget-settings">
    <el-card shadow="never" class="filter-card">
      <div class="filter-header">
        <span class="title">预算编制</span>
      </div>
      <el-form :inline="true" class="filter-form">
        <el-form-item label="门店">
          <StoreSelect v-model="storeId" width="200px" @change="handleStoreChange" />
        </el-form-item>
        <el-form-item label="月份">
          <el-date-picker
            v-model="monthDate"
            type="month"
            placeholder="选择月份"
            format="YYYY年MM月"
            value-format="YYYY-MM-DD"
            :clearable="false"
            @change="fetchData"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="fetchData">加载数据</el-button>
          <el-button type="success" :loading="saving" @click="handleSave">保存预算</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card shadow="never" class="content-card">
      <el-table v-loading="loading" :data="budgetItems" border style="width: 100%" height="calc(100vh - 240px)">
        <el-table-column prop="expense_type_name" label="费用科目" width="200" />
        <el-table-column prop="expense_category" label="分类" width="150">
           <template #default="{ row }">
             <el-tag size="small">{{ row.category || '默认' }}</el-tag>
           </template>
        </el-table-column>
        <el-table-column label="本月预算金额 (元)">
          <template #default="{ row }">
            <el-input-number 
              v-model="row.amount" 
              :precision="2" 
              :step="100" 
              :min="0" 
              style="width: 100%" 
              controls-position="right"
            />
          </template>
        </el-table-column>
        <el-table-column label="历史参考" width="200">
           <template #default="{ row }">
              <span class="info-text">上次设定: ¥{{ formatAmount(row.last_amount) }}</span>
           </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import StoreSelect from '@/components/StoreSelect.vue'
import { getExpenseTypeList } from '@/api/expense'
import { getBudgetAnalysis, batchSaveBudgets } from '@/api/budget'
import type { ExpenseTypeInfo } from '@/types'

const storeId = ref<number>()
const monthDate = ref(dayjs().format('YYYY-MM-01'))
const loading = ref(false)
const saving = ref(false)
const expenseTypes = ref<ExpenseTypeInfo[]>([])

// 界面展示用的数据项
interface BudgetItemUI {
  expense_type_id: number
  expense_type_name: string
  category?: string
  amount: number
  last_amount: number // 这里简化处理，暂且用预算分析接口返回的 actual_amount 或者 budget_amount 填充
}

const budgetItems = ref<BudgetItemUI[]>([])

const year = computed(() => dayjs(monthDate.value).year())
const month = computed(() => dayjs(monthDate.value).month() + 1)

function formatAmount(val: number) {
  return val ? val.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) : '0.00'
}

function handleStoreChange() {
  if (storeId.value) {
    fetchData()
  }
}

async function fetchData() {
  if (!storeId.value) {
    ElMessage.warning('请选择门店')
    return
  }
  
  loading.value = true
  try {
    // 1. 获取所有费用科目
    // 如果 expenseTypes 为空则获取
    if (expenseTypes.value.length === 0) {
      const res = await getExpenseTypeList()
      if (res.code === 0 || res.code === 200) {
        expenseTypes.value = res.data
      }
    }
    
    // 2. 获取当前已有的预算数据 (通过分析接口获取，因为分析接口返回 budget_amount)
    const resAnalysis = await getBudgetAnalysis({
      store_id: storeId.value,
      year: year.value,
      month: month.value
    })
    
    let existingBudgets: Record<number, number> = {}
    if ((resAnalysis.code === 0 || resAnalysis.code === 200) && resAnalysis.data) {
      resAnalysis.data.items.forEach(item => {
        existingBudgets[item.expense_type_id] = item.budget_amount
      })
    }

    // 3. 构建表格数据
    budgetItems.value = expenseTypes.value.map(et => ({
      expense_type_id: et.id,
      expense_type_name: et.name,
      category: et.category,
      amount: existingBudgets[et.id] || 0,
      last_amount: 0 // TODO: 如果需要显示上月数据，需要额外请求
    }))
    
  } catch (error) {
    console.error(error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

async function handleSave() {
  if (!storeId.value) return
  
  saving.value = true
  try {
    const items = budgetItems.value.map(item => ({
      expense_type_id: item.expense_type_id,
      amount: item.amount
    }))
    
    const res = await batchSaveBudgets({
      store_id: storeId.value,
      year: year.value,
      month: month.value,
      items: items
    })
    
    if (res.code === 0 || res.code === 200) {
      ElMessage.success('预算保存成功')
      fetchData() // 刷新
    } else {
      ElMessage.error(res.message || '保存失败')
    }
  } catch (error) {
    console.error(error)
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped lang="scss">
.budget-settings {
  padding: 20px;
}
.filter-card {
  margin-bottom: 20px;
  .filter-header {
    margin-bottom: 15px;
    font-weight: bold;
    font-size: 16px;
  }
}
.info-text {
  color: #909399;
  font-size: 12px;
}
</style>
