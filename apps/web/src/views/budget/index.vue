<template>
  <div class="budget-container">
    <section class="analysis-page-head">
      <div>
        <p class="eyebrow">Budget Control</p>
        <h1>预算管理</h1>
      </div>
      <span>{{ DEMO_PERIOD.label }} 预算执行和差异分析</span>
    </section>

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
            class="form-input-sm"
            @change="handleQuery"
          />
        </el-form-item>

        <el-form-item label="月份">
          <el-select
            v-model="queryForm.month"
            placeholder="选择月份"
            clearable
            class="form-input-sm"
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

        <el-form-item class="filter-actions">
          <div class="action-cluster action-cluster--query">
            <el-button
              type="primary"
              :icon="Search"
              class="financial-button financial-button--primary financial-button--medium"
              @click="handleQuery"
            >
              查询
            </el-button>
            <el-button
              :icon="Refresh"
              class="financial-button financial-button--outline financial-button--medium"
              @click="handleReset"
            >
              重置
            </el-button>
          </div>
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
            style="margin-bottom: var(--spacing-5)"
          />

          <el-table
            v-else
            v-loading="budgetLoading"
            :data="budgetTableData"
            stripe
            border
            :header-cell-style="{ background: 'var(--color-gray-50)', color: 'var(--color-text-secondary)' }"
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
                  class="budget-input"
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
            style="margin-bottom: var(--spacing-5)"
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
              :header-cell-style="{ background: 'var(--color-gray-50)', color: 'var(--color-text-secondary)' }"
              style="margin-top: var(--spacing-5)"
            >
              <el-table-column type="index" label="序号" width="60" align="center" />
              <el-table-column prop="expense_type_name" label="费用科目" min-width="120" />
              <el-table-column prop="budget_amount" label="预算金额" width="150" align="right">
                <template #default="{ row }">
                  <span class="budget-amount-cell">
                    ¥{{ formatNumber(row.budget_amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="actual_amount" label="实际金额" width="150" align="right">
                <template #default="{ row }">
                  <span :class="['actual-amount-cell', row.is_over_budget ? 'over-budget' : 'under-budget']">
                    ¥{{ formatNumber(row.actual_amount) }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="variance" label="差异额" width="150" align="right">
                <template #default="{ row }">
                  <span :class="['variance-cell', row.variance >= 0 ? 'positive' : 'negative']">
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
import type { BudgetAnalysisItem, BudgetAnalysisResponse, BudgetItemInput } from '@/types/modules/budget'
import { DEMO_PERIOD, PERMISSIONS } from '@/config'

// 状态
const activeTab = ref('setting')
const budgetLoading = ref(false)
const analysisLoading = ref(false)
const saveLoading = ref(false)

// 查询表单
const queryForm = reactive({
  store_id: undefined as number | undefined,
  year: DEMO_PERIOD.year,
  month: DEMO_PERIOD.month
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

const fallbackBudgetRows: BudgetAnalysisItem[] = [
  { expense_type_id: 1, expense_type_name: '人工成本', budget_amount: 385000, actual_amount: 412360, variance: 27360, variance_rate: 7.11, is_over_budget: true },
  { expense_type_id: 2, expense_type_name: '租金及物业', budget_amount: 142000, actual_amount: 138540, variance: -3460, variance_rate: -2.44, is_over_budget: false },
  { expense_type_id: 3, expense_type_name: '能源费用', budget_amount: 82000, actual_amount: 86730, variance: 4730, variance_rate: 5.77, is_over_budget: true },
  { expense_type_id: 4, expense_type_name: '营销费用', budget_amount: 70000, actual_amount: 65420, variance: -4580, variance_rate: -6.54, is_over_budget: false },
  { expense_type_id: 5, expense_type_name: '维修与低耗', budget_amount: 48000, actual_amount: 39680, variance: -8320, variance_rate: -17.33, is_over_budget: false },
]

const fallbackBudgetAnalysis: BudgetAnalysisResponse = {
  total_budget: fallbackBudgetRows.reduce((sum, item) => sum + item.budget_amount, 0),
  total_actual: fallbackBudgetRows.reduce((sum, item) => sum + item.actual_amount, 0),
  total_variance: fallbackBudgetRows.reduce((sum, item) => sum + item.variance, 0),
  items: fallbackBudgetRows,
}

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
    expenseTypeList.value = res.data.length ? res.data : fallbackBudgetRows.map(item => ({
      id: item.expense_type_id,
      code: `BUDGET_${item.expense_type_id}`,
      name: item.expense_type_name,
      category: '预算科目',
      description: `${DEMO_PERIOD.label} 样例预算科目`,
      is_active: true
    } as ExpenseTypeInfo))
    
    // 初始化预算表格数据
    budgetTableData.value = expenseTypeList.value.map((type: ExpenseTypeInfo) => ({
      id: type.id,
      name: type.name,
      description: type.description || '',
      amount: fallbackBudgetRows.find(item => item.expense_type_id === type.id)?.budget_amount ?? 0
    }))
  } catch (error) {
    ElMessage.warning('费用科目接口暂无可用数据，已显示本地预算样例')
    expenseTypeList.value = fallbackBudgetRows.map(item => ({
      id: item.expense_type_id,
      code: `BUDGET_${item.expense_type_id}`,
      name: item.expense_type_name,
      category: '预算科目',
      description: `${DEMO_PERIOD.label} 样例预算科目`,
      is_active: true
    } as ExpenseTypeInfo))
    budgetTableData.value = fallbackBudgetRows.map(item => ({
      id: item.expense_type_id,
      name: item.expense_type_name,
      description: `${DEMO_PERIOD.label} 预算控制样例`,
      amount: item.budget_amount
    }))
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
  queryForm.year = DEMO_PERIOD.year
  queryForm.month = DEMO_PERIOD.month
  analysisData.value = fallbackBudgetAnalysis
  budgetTableData.value.forEach(row => {
    row.amount = fallbackBudgetRows.find(item => item.expense_type_id === row.id)?.budget_amount ?? 0
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
  if (!queryForm.year || !queryForm.month) {
    ElMessage.warning('请选择年份和月份')
    return
  }

  try {
    analysisLoading.value = true
    const res = await budgetApi.getBudgetAnalysis({
      store_id: queryForm.store_id ?? 1,
      year: parseInt(queryForm.year),
      month: queryForm.month
    })
    const data = res.data
    const hasData = data?.items?.some(item => Math.abs(item.budget_amount || 0) + Math.abs(item.actual_amount || 0) > 0)
    analysisData.value = hasData ? data : fallbackBudgetAnalysis
  } catch {
    ElMessage.warning('预算分析接口暂无可用经营数据，已显示本地样例')
    analysisData.value = fallbackBudgetAnalysis
  } finally {
    analysisLoading.value = false
  }
}

// 页面加载
onMounted(() => {
  loadExpenseTypes()
  analysisData.value = fallbackBudgetAnalysis
})
</script>

<style scoped lang="scss">
.budget-container {
  padding: 0;
  min-height: 100%;

  .analysis-page-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 16px;
    margin-bottom: 12px;

    h1 {
      margin: 2px 0 0;
      color: #211A15;
      font-size: 22px;
      font-weight: 900;
    }

    > span {
      color: #8A8074;
      font-size: 12px;
      font-weight: 700;
    }
  }

  .eyebrow {
    margin: 0;
    color: #8A8074;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0;
  }

  .filter-card {
    margin-bottom: 12px;
  }

  .tabs-container {
    padding: 16px;
    border: 1px solid #E5DED4;
    border-radius: 6px;
    background: rgba(255, 253, 249, 0.96);
    box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-4) 0;
  }

  // 汇总统计
  .summary-section {
    margin-bottom: var(--spacing-5);

    .summary-card {
      background: var(--color-bg-primary);
      color: var(--color-text-primary);
      padding: var(--spacing-5);
      border-radius: 6px;
      border: 1px solid #E5DED4;
      box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
      transition: all var(--transition-duration-base) var(--transition-timing-function-base);
      height: 100%;

      &:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--color-border-primary);
      }

      .label {
        font-size: var(--font-size-sm);
        color: var(--color-text-tertiary);
        margin-bottom: var(--spacing-2);
        text-transform: uppercase;
        letter-spacing: 0;
        font-weight: var(--font-weight-medium);
      }

      .value {
        font-size: var(--font-size-2xl);
        font-weight: var(--font-weight-bold);
        line-height: 1.2;
      }

      // 预算卡片 - 使用主色调
      &.budget {
        .value {
          color: var(--color-primary);
        }
      }

      // 实际卡片 - 使用信息色调
      &.actual {
        .value {
          color: var(--color-info);
        }
      }

      // 差异卡片 - 根据超支/节省状态变化
      &.variance {
        &.over {
          .value {
            color: var(--color-danger);
          }
        }

        &.under {
          .value {
            color: var(--color-success);
          }
        }
      }

      // 差异率卡片 - 与差异卡片保持一致
      &.rate {
        &.over {
          .value {
            color: var(--color-danger);
          }
        }

        &.under {
          .value {
            color: var(--color-success);
          }
        }
      }
    }
  }

  // ===== 筛选卡片样式 =====
  .filter-card {
    margin-bottom: 12px;
    border-radius: 6px;
    border: 1px solid #E5DED4;
    background: rgba(255, 253, 249, 0.96);
    box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
    transition: box-shadow var(--transition-duration-base) var(--transition-timing-function-base);

    &:hover {
      box-shadow: var(--shadow-md);
    }

    :deep(.el-card__body) {
      padding: 14px;
    }

    :deep(.el-form) {
      margin: 0;
      display: flex;
      flex-wrap: wrap;
      gap: var(--spacing-4);
      align-items: center;

      .el-form-item {
        margin: 0;
        margin-bottom: 0;

        &.filter-actions {
          flex: 1;
          display: flex;
          justify-content: flex-end;
          gap: var(--spacing-2);
        }
      }

      // 小尺寸表单输入
      .form-input-sm {
        width: calc(var(--spacing-6) * 3.75); // 120px

        :deep(.el-input__wrapper) {
          border-radius: var(--border-radius-sm);
          border: 1px solid #D7CEC2;
          background-color: #FFFDF9;
          transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

          &:hover {
            border-color: var(--color-border-base);
          }

          &.is-focus {
            border-color: var(--color-primary);
            box-shadow: 0 0 0 1px var(--color-primary-lightest);
          }
        }

        // 日期选择器特殊处理
        &.el-date-editor {
          :deep(.el-input__wrapper) {
            .el-range__icon,
            .el-input__icon {
              color: var(--color-text-tertiary);
            }
          }
        }
      }
    }

    @media (max-width: var(--breakpoint-md)) {
      :deep(.el-form) {
        .el-form-item {
          width: calc(50% - var(--spacing-4));

          &.filter-actions {
            width: 100%;
            justify-content: flex-start;
          }
        }
      }
    }

    @media (max-width: var(--breakpoint-sm)) {
      :deep(.el-form) {
        .el-form-item {
          width: 100%;

          &.filter-actions {
            width: 100%;
            justify-content: flex-start;
          }
        }
      }
    }
  }

  // ===== 标签页样式 =====
  :deep(.el-tabs) {
    .el-tabs__header {
      background: transparent;
      border-radius: 0;
      border-bottom: 1px solid #E5DED4;
      padding: 0 var(--spacing-5);

      .el-tabs__nav-wrap {
        &:after {
          background-color: var(--color-border-light);
        }
      }

      .el-tabs__item {
        color: #695F55;
        font-weight: 800;
        padding: var(--spacing-3) var(--spacing-4);
        transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

        &:hover {
          color: var(--color-text-primary);
        }

        &.is-active {
          color: #C81E1E;
          font-weight: 900;
        }
      }

      .el-tabs__active-bar {
        background-color: #C81E1E;
        height: var(--border-width-thick);
      }
    }

    .el-tabs__content {
      background: transparent;
      border-radius: 0;
      padding: var(--spacing-5);
    }
  }

  // ===== 卡片统一样式 =====
  :deep(.el-card:not(.filter-card)) {
    border-radius: 6px;
    border: 1px solid #E5DED4;
    background: rgba(255, 253, 249, 0.98);
    box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
    transition: box-shadow var(--transition-duration-base) var(--transition-timing-function-base);
    overflow: hidden;

    &:hover {
      box-shadow: var(--shadow-md);
    }

    .el-card__header {
      background-color: #F8F2EA;
      border-bottom: 1px solid #E5DED4;
      padding: var(--spacing-4) var(--spacing-5);

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0;
      }
    }

    .el-card__body {
      padding: var(--spacing-5);
    }
  }

  // ===== 数据表格统一样式 =====
  :deep(.el-table) {
    border-radius: var(--border-radius-sm);
    overflow: hidden;
    border: var(--border-width-thin) solid var(--color-border-light);

    &.el-table--border {
      border: var(--border-width-thin) solid var(--color-border-light);
    }

    &.el-table--striped {
      .el-table__body {
        tr.el-table__row--striped {
          td {
            background-color: var(--color-bg-secondary);
          }

          &:hover {
            td {
              background-color: var(--color-gray-50);
            }
          }
        }
      }
    }

    // 表头样式
    .el-table__header-wrapper {
      th {
        background-color: var(--color-bg-secondary) !important;
        color: var(--color-text-secondary) !important;
        font-weight: var(--font-weight-semibold);
        font-size: var(--font-size-sm);
        text-transform: uppercase;
        letter-spacing: 0;
        border-bottom: var(--border-width-thin) solid var(--color-border-base);
        padding: var(--spacing-3) var(--spacing-3);

        .cell {
          line-height: 1.4;
        }
      }
    }

    // 表格主体
    .el-table__body-wrapper {
      .el-table__row {
        transition: background-color var(--transition-duration-fast) var(--transition-timing-function-base);

        &:hover {
          td {
            background-color: var(--color-bg-tertiary);
          }
        }

        td {
          padding: var(--spacing-3) var(--spacing-3);
          border-bottom: var(--border-width-thin) solid var(--color-border-light);
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          line-height: 1.5;

          &:first-child {
            color: var(--color-text-tertiary);
            font-weight: var(--font-weight-medium);
          }
        }
      }
    }

    // 金额列样式 - 预算使用主色调，实际根据状态变化
    .el-table__row {
      .budget-amount-cell {
        font-weight: var(--font-weight-semibold);
        color: var(--color-primary);
      }

      .actual-amount-cell {
        font-weight: var(--font-weight-semibold);

        &.over-budget {
          color: var(--color-danger);
        }

        &.under-budget {
          color: var(--color-success);
        }
      }

      .variance-cell {
        font-weight: var(--font-weight-semibold);

        &.positive {
          color: var(--color-danger);
        }

        &.negative {
          color: var(--color-success);
        }
      }
    }

    // 操作按钮
    .el-button {
      transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

      &:hover {
        transform: translateY(-1px);
      }

      &.el-button--link {
        padding: var(--spacing-1) var(--spacing-2);
        font-size: var(--font-size-xs);
      }
    }

    // 预算输入框样式
    .budget-input {
      width: calc(var(--spacing-6) * 5.625); // 180px

      :deep(.el-input__wrapper) {
        border-radius: var(--border-radius-sm);
        border: var(--border-width-thin) solid var(--color-border-light);
        background-color: var(--color-bg-primary);
        transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

        &:hover {
          border-color: var(--color-border-base);
        }

        &.is-focus {
          border-color: var(--color-primary);
          box-shadow: 0 0 0 1px var(--color-primary-lightest);
        }
      }
    }
  }

  // ===== 警报统一样式 =====
  :deep(.el-alert) {
    border-radius: var(--border-radius-sm);
    border: var(--border-width-thin) solid var(--color-border-light);
    background-color: var(--color-bg-secondary);

    .el-alert__title {
      color: var(--color-text-primary);
      font-weight: var(--font-weight-medium);
    }

    .el-alert__description {
      color: var(--color-text-secondary);
      font-size: var(--font-size-sm);
    }
  }

  // ===== 加载状态 =====
  :deep(.el-loading-mask) {
    background-color: rgba(var(--color-bg-primary-rgb), 0.8);
    backdrop-filter: blur(4px);

    .el-loading-spinner {
      .circular {
        .path {
          stroke: var(--color-primary);
        }
      }

      .el-loading-text {
        color: var(--color-text-secondary);
        margin-top: var(--spacing-2);
        font-size: var(--font-size-sm);
      }
    }
  }

  // ===== 响应式调整 =====
  @media (max-width: var(--breakpoint-md)) {
    padding: var(--spacing-4);

    .summary-section {
      .el-row {
        flex-direction: column;
        gap: var(--spacing-3);

        .el-col {
          width: 100%;
        }
      }
    }

    .tabs-container {
      padding: var(--spacing-4);
    }

    :deep(.el-table) {
      .el-table__header-wrapper,
      .el-table__body-wrapper {
        overflow-x: auto;

        th,
        td {
          white-space: nowrap;
        }
      }
    }
  }

  @media (max-width: var(--breakpoint-sm)) {
    padding: var(--spacing-3);

    .tabs-container {
      padding: var(--spacing-3);
    }

    .filter-card {
      :deep(.el-form) {
        .el-form-item {
          width: 100%;
        }
      }
    }

    :deep(.el-card) {
      .el-card__header {
        padding: var(--spacing-3) var(--spacing-4);
      }

      .el-card__body {
        padding: var(--spacing-4);
      }
    }
  }
}
</style>
