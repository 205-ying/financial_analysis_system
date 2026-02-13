<template>
  <div class="budget-container">
    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" :inline="true" label-width="80px">
        <el-form-item label="门店">
          <StoreSelect v-model="queryForm.store_id" width="200px" @change="handleStoreChange" />
        </el-form-item>

        <el-form-item label="年份">
          <el-date-picker
            v-model="queryForm.year"
            type="year"
            placeholder="选择年份"
            value-format="YYYY"
            style="width: 120px"
            @change="handleQuery"
          />
        </el-form-item>

        <el-form-item label="月份">
          <el-select
            v-model="queryForm.month"
            placeholder="选择月份"
            clearable
            style="width: 120px"
            @change="handleQuery"
          >
            <el-option
              v-for="month in 12"
              :key="month"
              :label="`${month}月`"
              :value="month"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 标签页 -->
    <el-tabs v-model="activeTab" class="tabs-container">
      <!-- 预算设置 -->
      <el-tab-pane label="预算设置" name="setting">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>预算设置</span>
              <el-button
                v-permission="PERMISSIONS.BUDGET_MANAGE"
                type="primary"
                :icon="Plus"
                size="small"
                :loading="saveLoading"
                @click="handleSaveBudgets"
              >
                保存预算
              </el-button>
            </div>
          </template>

          <el-alert
            v-if="!queryForm.store_id || !queryForm.year || !queryForm.month"
            title="请先选择门店、年份和月份"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px"
          />

          <el-table
            v-else
            v-loading="budgetLoading"
            :data="budgetTableData"
            stripe
            border
            :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
          >
            <el-table-column type="index" label="序号" width="60" align="center" />
            <el-table-column prop="name" label="费用科目" min-width="150" />
            <el-table-column label="预算金额（元）" width="200" align="center">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.amount"
                  :min="0"
                  :max="99999999"
                  :precision="2"
                  :step="1000"
                  controls-position="right"
                  style="width: 180px"
                />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" min-width="200" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 差异分析 -->
      <el-tab-pane label="差异分析" name="analysis">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>预算差异分析</span>
              <el-button
                type="primary"
                :icon="Refresh"
                size="small"
                :loading="analysisLoading"
                @click="handleAnalysis"
              >
                刷新分析
              </el-button>
            </div>
          </template>

          <el-alert
            v-if="!queryForm.store_id || !queryForm.year || !queryForm.month"
            title="请先选择门店、年份和月份"
            type="info"
            :closable="false"
            show-icon
            style="margin-bottom: 20px"
          />

          <div v-else>
            <!-- 汇总统计 -->
            <div v-if="analysisData" class="summary-section">
              <el-row :gutter="16">
                <el-col :span="6">
                  <div class="summary-card budget">
                    <div class="label">总预算</div>
                    <div class="value">¥{{ formatNumber(analysisData.total_budget) }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-card actual">
                    <div class="label">总实际</div>
                    <div class="value">¥{{ formatNumber(analysisData.total_actual) }}</div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-card variance" :class="varianceClass">
                    <div class="label">总差异</div>
                    <div class="value">
                      {{ analysisData.total_variance >= 0 ? '+' : '' }}¥{{ formatNumber(analysisData.total_variance) }}
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="summary-card rate" :class="varianceClass">
                    <div class="label">差异率</div>
                    <div class="value">
                      {{ analysisData.total_budget > 0 
                        ? (analysisData.total_variance / analysisData.total_budget * 100).toFixed(2) 
                        : '0.00' 
                      }}%
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 明细表格 -->
            <el-table
              v-loading="analysisLoading"
              :data="analysisData?.items || []"
              stripe
              border
              :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
              style="margin-top: 20px"
            >
              <el-table-column type="index" label="序号" width="60" align="center" />
              <el-table-column prop="expense_type_name" label="费用科目" min-width="120" />
              <el-table-column prop="budget_amount" label="预算金额" width="150" align="right">
                <template #default="{ row }">
                  ¥{{ formatNumber(row.budget_amount) }}
                </template>
              </el-table-column>
              <el-table-column prop="actual_amount" label="实际金额" width="150" align="right">
                <template #default="{ row }">
                  <span :style="{ color: row.is_over_budget ? '#f56c6c' : '#67c23a', fontWeight: 600 }">
                    ¥{{ formatNumber(row.actual_amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="variance" label="差异额" width="150" align="right">
                <template #default="{ row }">
                  <span :style="{ color: row.variance >= 0 ? '#f56c6c' : '#67c23a' }">
                    {{ row.variance >= 0 ? '+' : '' }}¥{{ formatNumber(row.variance) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="variance_rate" label="差异率" width="120" align="center">
                <template #default="{ row }">
                  <el-tag :type="getVarianceTagType(row.variance_rate)" size="small">
                    {{ row.variance_rate >= 0 ? '+' : '' }}{{ row.variance_rate.toFixed(2) }}%
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_over_budget" label="状态" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.is_over_budget ? 'danger' : 'success'" size="small">
                    {{ row.is_over_budget ? '超支' : '正常' }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Plus } from '@element-plus/icons-vue'
import StoreSelect from '@/components/StoreSelect.vue'
import { budgetApi } from '@/api'
import { getExpenseTypeList } from '@/api/expense'
import type { ExpenseTypeInfo } from '@/types'
import type { BudgetAnalysisResponse, BudgetItemInput } from '@/types/modules/budget'
import { PERMISSIONS } from '@/config'

// 状态
const activeTab = ref('setting')
const budgetLoading = ref(false)
const analysisLoading = ref(false)
const saveLoading = ref(false)

// 查询表单
const queryForm = reactive({
  store_id: undefined as number | undefined,
  year: new Date().getFullYear().toString(),
  month: new Date().getMonth() + 1
})

// 费用科目列表
const expenseTypeList = ref<ExpenseTypeInfo[]>([])

// 预算表格数据
interface BudgetTableRow {
  id: number
  name: string
  description: string
  amount: number
}
const budgetTableData = ref<BudgetTableRow[]>([])

// 分析数据
const analysisData = ref<BudgetAnalysisResponse | null>(null)

// 计算差异样式
const varianceClass = computed(() => {
  if (!analysisData.value) return ''
  return analysisData.value.total_variance > 0 ? 'over' : 'under'
})

// 格式化数字
const formatNumber = (value: number) => {
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// 获取差异率标签类型
const getVarianceTagType = (rate: number) => {
  if (rate > 10) return 'danger'
  if (rate > 5) return 'warning'
  if (rate < -5) return 'success'
  return 'info'
}

// 加载费用科目
const loadExpenseTypes = async () => {
  try {
    const res = await getExpenseTypeList()
    expenseTypeList.value = res.data
    
    // 初始化预算表格数据
    budgetTableData.value = expenseTypeList.value.map((type: ExpenseTypeInfo) => ({
      id: type.id,
      name: type.name,
      description: type.description || '',
      amount: 0
    }))
  } catch (error) {
    ElMessage.error('加载费用科目失败')
  }
}

// 门店变化
const handleStoreChange = () => {
  // 切换门店时清空数据
  analysisData.value = null
  if (budgetTableData.value.length > 0) {
    budgetTableData.value.forEach(row => {
      row.amount = 0
    })
  }
}

// 查询
const handleQuery = () => {
  if (activeTab.value === 'analysis') {
    handleAnalysis()
  }
}

// 重置
const handleReset = () => {
  queryForm.store_id = undefined
  queryForm.year = new Date().getFullYear().toString()
  queryForm.month = new Date().getMonth() + 1
  analysisData.value = null
  budgetTableData.value.forEach(row => {
    row.amount = 0
  })
}

// 保存预算
const handleSaveBudgets = async () => {
  if (!queryForm.store_id) {
    ElMessage.warning('请选择门店')
    return
  }
  if (!queryForm.year || !queryForm.month) {
    ElMessage.warning('请选择年份和月份')
    return
  }

  // 过滤掉金额为0的项
  const items: BudgetItemInput[] = budgetTableData.value
    .filter(row => row.amount > 0)
    .map(row => ({
      expense_type_id: row.id,
      amount: row.amount
    }))

  if (items.length === 0) {
    ElMessage.warning('请至少设置一项预算')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确认保存 ${queryForm.year}年${queryForm.month}月 的预算设置？`,
      '确认保存',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    saveLoading.value = true
    await budgetApi.batchSaveBudgets({
      store_id: queryForm.store_id,
      year: parseInt(queryForm.year),
      month: queryForm.month,
      items
    })

    ElMessage.success('预算保存成功')
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error(error instanceof Error ? error.message : '保存预算失败')
    }
  } finally {
    saveLoading.value = false
  }
}

// 预算差异分析
const handleAnalysis = async () => {
  if (!queryForm.store_id) {
    ElMessage.warning('请选择门店')
    return
  }
  if (!queryForm.year || !queryForm.month) {
    ElMessage.warning('请选择年份和月份')
    return
  }

  try {
    analysisLoading.value = true
    const res = await budgetApi.getBudgetAnalysis({
      store_id: queryForm.store_id,
      year: parseInt(queryForm.year),
      month: queryForm.month
    })
    analysisData.value = res.data
  } catch {
    ElMessage.error('获取预算分析失败')
  } finally {
    analysisLoading.value = false
  }
}

// 页面加载
onMounted(() => {
  loadExpenseTypes()
})
</script>

<style scoped lang="scss">
.budget-container {
  padding: 20px;

  .filter-card {
    margin-bottom: 20px;
  }

  .tabs-container {
    background: #fff;
    padding: 20px;
    border-radius: 4px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  // 汇总统计
  .summary-section {
    .summary-card {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: #fff;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);

      .label {
        font-size: 14px;
        opacity: 0.9;
        margin-bottom: 10px;
      }

      .value {
        font-size: 24px;
        font-weight: bold;
      }

      &.budget {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      }

      &.actual {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
      }

      &.variance {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);

        &.over {
          background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }

        &.under {
          background: linear-gradient(135deg, #30cfd0 0%, #330867 100%);
        }
      }

      &.rate {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;

        &.over {
          background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        }

        &.under {
          background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);
        }
      }
    }
  }
}
</style>
