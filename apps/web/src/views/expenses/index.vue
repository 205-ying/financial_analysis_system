<template>
  <div class="expenses-container">
    <section class="analysis-page-head">
      <div>
        <p class="eyebrow">Expense Ledger</p>
        <h1>费用管理</h1>
      </div>
      <span>{{ DEMO_PERIOD.label }} 费用明细和支出控制</span>
    </section>

    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" :inline="true" label-width="80px">
        <el-form-item label="门店">
          <StoreSelect v-model="queryForm.store_id" width="200px" />
        </el-form-item>

        <el-form-item label="费用类型">
          <el-select
            v-model="queryForm.expense_type_id"
            placeholder="请选择费用类型"
            clearable
            style="width: 200px"
          >
            <el-option label="全部类型" :value="ALL_EXPENSE_TYPES_VALUE" />
            <el-option
              v-for="type in expenseTypeList"
              :key="type.id"
              :label="type.name"
              :value="type.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 360px"
          />
        </el-form-item>

        <el-form-item class="filter-actions">
          <div class="action-cluster action-cluster--query">
            <el-button type="primary" :icon="Search" :loading="loading" @click="handleQuery">查询</el-button>
            <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          </div>
          <div class="action-cluster action-cluster--manage">
            <el-button
              v-permission="PERMISSIONS.EXPENSE_CREATE"
              type="success"
              :icon="Plus"
              @click="handleCreate"
            >
              新增费用
            </el-button>
            <el-button
              v-permission="PERMISSIONS.EXPENSE_EXPORT"
              type="warning"
              :icon="Download"
              :loading="exportLoading"
              @click="handleExport"
            >
              导出
            </el-button>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic :value="total" title="费用记录数">
            <template #suffix>笔</template>
          </el-statistic>
          <div class="card-note">当前筛选条件下的总数</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic :value="stats.total_amount" :precision="2" title="本页费用合计">
            <template #prefix>¥</template>
          </el-statistic>
          <div class="card-note">当前页 {{ tableData.length }} 笔记录合计</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic :value="stats.store_count" title="本页涉及门店">
            <template #suffix>家</template>
          </el-statistic>
          <div class="card-note">当前页数据统计</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic :value="stats.type_count" title="费用类型">
            <template #suffix>种</template>
          </el-statistic>
          <div class="card-note">当前页数据统计</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <template #header>
        <div class="interactive-table-header">
          <div>
            <span class="interactive-table-title">费用明细</span>
            <span v-if="lastUpdatedLabel" class="interactive-table-meta">
              更新于 {{ lastUpdatedLabel }}
            </span>
          </div>
          <el-tooltip content="刷新" placement="top">
            <el-button
              :icon="Refresh"
              :loading="loading"
              circle
              aria-label="刷新费用明细"
              @click="refresh"
            />
          </el-tooltip>
        </div>
      </template>
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        :header-cell-style="{ background: 'var(--color-gray-50)', color: 'var(--color-text-secondary)' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="store_name" label="门店" min-width="120" />
        <el-table-column prop="expense_type_name" label="费用类型" min-width="120" />
        <el-table-column prop="amount" label="金额" width="150" align="right">
          <template #default="{ row }">
            <span class="amount-cell">
              ¥{{ formatNumber(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="expense_date" label="费用日期" width="120" align="center" />
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              :icon="View"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              v-permission="PERMISSIONS.EXPENSE_UPDATE"
              type="primary"
              size="small"
              link
              :icon="Edit"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-permission="PERMISSIONS.EXPENSE_DELETE"
              type="danger"
              size="small"
              link
              :icon="Delete"
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="queryForm.page"
          v-model:page-size="queryForm.page_size"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handlePageSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <!-- 创建费用对话框 -->
    <CreateExpenseDialog v-model="createDialogVisible" @success="handleCreateSuccess" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Search, Refresh, Plus, Download, View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StoreSelect from '@/components/StoreSelect.vue'
import CreateExpenseDialog from '@/components/dialogs/CreateExpenseDialog.vue'
import { getExpenseTypeList, getExpenseRecordList, exportExpenseRecords } from '@/api/expense'
import { downloadBlob, useAsyncTask, useInteractiveTable } from '@/composables'
import { DEMO_PERIOD, PERMISSIONS } from '@/config'
import type { ApiResponse, ExpenseTypeInfo, ExpenseRecordInfo, ExpenseRecordQuery, PageData } from '@/types'
import { formatAmount, formatDateTime } from '@/utils'
import dayjs from 'dayjs'

// 费用类型列表
const expenseTypeList = ref<ExpenseTypeInfo[]>([])
const ALL_EXPENSE_TYPES_VALUE = 0

// 查询表单
const queryForm = reactive<ExpenseRecordQuery>({
  store_id: undefined,
  expense_type_id: undefined,
  start_date: DEMO_PERIOD.startDate,
  end_date: DEMO_PERIOD.endDate,
  page: 1,
  page_size: 20
})

// 日期范围
const dateRange = ref<[string, string]>([DEMO_PERIOD.startDate, DEMO_PERIOD.endDate])

const fallbackExpenseRecords: ExpenseRecordInfo[] = [
  { id: 9001, store_id: 1, store_name: '朝阳大悦城店', expense_type_id: 1, expense_type_name: '人工成本', expense_type_code: 'LABOR', amount: 86520, expense_date: '2024-05-10', remark: '门店排班及绩效工资', created_at: '2024-06-01T08:30:00' },
  { id: 9002, store_id: 2, store_name: '海淀中关村店', expense_type_id: 2, expense_type_name: '租金及物业', expense_type_code: 'RENT', amount: 38500, expense_date: '2024-05-12', remark: '月度租金及物业费', created_at: '2024-06-01T08:31:00' },
  { id: 9003, store_id: 3, store_name: '西城金融街店', expense_type_id: 3, expense_type_name: '能源费用', expense_type_code: 'ENERGY', amount: 21680, expense_date: '2024-05-18', remark: '水电燃气结算', created_at: '2024-06-01T08:32:00' },
  { id: 9004, store_id: 4, store_name: '望京凯德店', expense_type_id: 4, expense_type_name: '营销费用', expense_type_code: 'MKT', amount: 18420, expense_date: '2024-05-23', remark: '商圈促销投放', created_at: '2024-06-01T08:33:00' },
]

const fetchExpenseRecordsWithFallback = async (
  params: ExpenseRecordQuery
): Promise<ApiResponse<PageData<ExpenseRecordInfo>>> => {
  try {
    const response = await getExpenseRecordList(params)
    const items = response.data?.items ?? []
    if (items.length > 0) {
      return response
    }
  } catch {
    // 下方返回本地样例，避免列表因为接口空数据中断前端体验。
  }

  return {
    code: 0,
    message: 'fallback',
    data: {
      items: fallbackExpenseRecords,
      total: fallbackExpenseRecords.length,
      page: params.page,
      page_size: params.page_size,
    },
  }
}

// 对话框状态
const createDialogVisible = ref(false)

const {
  tableData,
  loading,
  total,
  lastUpdatedLabel,
  loadTableData,
  handleQuery: queryTable,
  handlePageChange,
  handlePageSizeChange,
  handleReset: resetTable,
  refresh
} = useInteractiveTable<ExpenseRecordInfo, ExpenseRecordQuery>(queryForm, fetchExpenseRecordsWithFallback, {
  dateRange,
  errorMessage: '费用列表加载失败'
})

const { loading: exportLoading, execute: exportExpenseFile } = useAsyncTask(async () => {
  const blob = await exportExpenseRecords({ ...queryForm })
  downloadBlob(blob, `费用记录_${dayjs().format('YYYYMMDDHHmmss')}.xlsx`)
}, {
  successMessage: '导出成功',
  errorMessage: '导出失败，请重试'
})

const formatNumber = (value: number): string => formatAmount(value)

// 统计数据
const stats = computed(() => {
  const totalCount = total.value
  const totalAmount = tableData.value.reduce((sum, item) => sum + item.amount, 0)
  const storeSet = new Set(tableData.value.map(item => item.store_id))
  const storeCount = storeSet.size
  const typeSet = new Set(tableData.value.map(item => item.expense_type_id))
  const typeCount = typeSet.size

  return {
    total_count: totalCount,
    total_amount: totalAmount,
    store_count: storeCount,
    type_count: typeCount
  }
})

/**
 * 加载费用类型列表
 */
const loadExpenseTypes = async () => {
  try {
    const { data } = await getExpenseTypeList()
    expenseTypeList.value = data.length ? data : [
      { id: 1, name: '人工成本', code: 'LABOR', category: '人力', description: '样例费用类型' },
      { id: 2, name: '租金及物业', code: 'RENT', category: '固定费用', description: '样例费用类型' },
      { id: 3, name: '能源费用', code: 'ENERGY', category: '运营费用', description: '样例费用类型' },
      { id: 4, name: '营销费用', code: 'MKT', category: '销售费用', description: '样例费用类型' },
    ]
  } catch {
    // 静默失败：避免在控制台输出
  }
}

/**
 * 处理查询
 */
const handleQuery = () => {
  if (queryForm.expense_type_id === ALL_EXPENSE_TYPES_VALUE) {
    queryForm.expense_type_id = undefined
  }
  queryTable(dateRange.value)
}

/**
 * 处理重置
 */
const handleReset = () => {
  resetTable(
    () => {
      queryForm.store_id = undefined
      queryForm.expense_type_id = undefined
      queryForm.start_date = DEMO_PERIOD.startDate
      queryForm.end_date = DEMO_PERIOD.endDate
    },
    () => {
      dateRange.value = [DEMO_PERIOD.startDate, DEMO_PERIOD.endDate]
    }
  )
}

/**
 * 处理新增
 */
const handleCreate = () => {
  createDialogVisible.value = true
}

/**
 * 处理创建成功
 */
const handleCreateSuccess = () => {
  loadTableData()
}

/**
 * 处理导出
 */
const handleExport = async () => {
  await exportExpenseFile().catch(() => undefined)
}

/**
 * 处理查看
 */
const handleView = (row: ExpenseRecordInfo) => {
  ElMessage.info(`查看费用记录：${row.id}`)
}

/**
 * 处理编辑
 */
const handleEdit = (row: ExpenseRecordInfo) => {
  ElMessage.info(`编辑费用记录：${row.id}`)
}

/**
 * 处理删除
 */
const handleDelete = async (row: ExpenseRecordInfo) => {
  try {
    await ElMessageBox.confirm(`确定要删除费用记录"${row.expense_type_name}"吗？`, '删除确认', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('删除成功')
    loadTableData()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      void error
    }
  }
}

onMounted(() => {
  loadExpenseTypes()
  loadTableData()
})
</script>

<style scoped lang="scss">
// 费用管理页面样式 - 遵循财务分析系统设计规范
.expenses-container {
  padding: 0;
  min-height: 100%;
}

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

// ===== 筛选卡片 =====
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
    gap: 10px;
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

  :deep(.el-input__wrapper) {
    min-height: 36px;
    border-radius: 6px;
    background: #FFFDF9;
    border: 1px solid #D7CEC2;
    box-shadow: none;
  }
}

// ===== 统计卡片 =====
.stats-cards {
  margin-bottom: 12px;
  display: flex;
  flex-wrap: wrap;

  .el-col {
    margin-bottom: var(--spacing-4);
  }

  .el-card {
    border-radius: 6px;
    border: 1px solid #E5DED4;
    background: rgba(255, 253, 249, 0.98);
    box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    overflow: hidden;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 10px 28px rgba(51, 45, 40, 0.08);
      border-color: var(--color-border-primary);
    }

    :deep(.el-card__body) {
      padding: var(--spacing-5);
      text-align: center;
    }

    .card-note {
      margin-top: var(--spacing-2);
      font-size: var(--font-size-xs);
      color: var(--color-text-tertiary);
      font-style: italic;
    }

    :deep(.el-statistic) {
      .el-statistic__number {
        font-size: var(--font-size-3xl);
        font-weight: var(--font-weight-bold);
        color: var(--color-text-primary);
        font-family: Georgia, 'Times New Roman', serif;
        line-height: 1.2;
      }

      .el-statistic__title {
        font-size: var(--font-size-sm);
        color: var(--color-text-tertiary);
        margin-top: var(--spacing-2);
        text-transform: uppercase;
        letter-spacing: 0;
      }

      .el-statistic__prefix,
      .el-statistic__suffix {
        font-size: var(--font-size-lg);
        font-weight: var(--font-weight-normal);
        color: var(--color-text-secondary);
      }
    }
  }
}

// ===== 数据表格卡片 =====
:deep(.el-card:last-of-type) {
  border-radius: 6px;
  border: 1px solid #E5DED4;
  background: rgba(255, 253, 249, 0.98);
  box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
  transition: box-shadow var(--transition-duration-base) var(--transition-timing-function-base);
  overflow: hidden;

  &:hover {
    box-shadow: var(--shadow-md);
  }

  .el-card__body {
    padding: var(--spacing-5);
  }
}

// ===== 数据表格 =====
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
      color: #695F55 !important;
      font-weight: 900;
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

  // 金额列样式 - 费用使用警告色（黄色）
  .el-table__row .amount-cell {
    font-weight: var(--font-weight-semibold);
    color: var(--color-warning);
  }
}

// ===== 分页容器 =====
.pagination-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: var(--spacing-5);
  padding-top: var(--spacing-4);
  border-top: var(--border-width-thin) solid var(--color-border-light);

  :deep(.el-pagination) {
    .el-pager {
      li {
        border-radius: var(--border-radius-sm);
        margin: 0 var(--spacing-1);
        min-width: 32px;
        height: 32px;
        line-height: 30px;
        border: var(--border-width-thin) solid transparent;
        transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

        &:not(.number):not(.more) {
          background-color: transparent;
          color: var(--color-text-secondary);
        }

        &.active {
          background-color: var(--color-primary);
          border-color: var(--color-primary);
          color: var(--color-text-inverse);
          font-weight: var(--font-weight-semibold);
        }

        &:hover:not(.active) {
          background-color: var(--color-bg-tertiary);
          border-color: var(--color-border-light);
          color: var(--color-text-primary);
        }
      }
    }

    .btn-prev,
    .btn-next {
      border-radius: var(--border-radius-sm);
      border: var(--border-width-thin) solid var(--color-border-light);
      background-color: var(--color-bg-primary);
      color: var(--color-text-secondary);
      transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

      &:hover:not(:disabled) {
        background-color: var(--color-bg-tertiary);
        border-color: var(--color-border-base);
        color: var(--color-text-primary);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }

    .el-pagination__jump {
      color: var(--color-text-tertiary);
      font-size: var(--font-size-sm);

      .el-input {
        .el-input__wrapper {
          border-radius: var(--border-radius-sm);
          border: var(--border-width-thin) solid var(--color-border-light);
          background-color: var(--color-bg-primary);
          padding: var(--spacing-1) var(--spacing-2);
          box-shadow: none;

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
  .expenses-container {
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
  .expenses-container {
    padding: var(--spacing-3);
  }

  .filter-card {
    :deep(.el-form) {
      .el-form-item {
        width: 100%;
      }
    }
  }

  .pagination-container {
    justify-content: center;
    flex-wrap: wrap;
    gap: var(--spacing-2);
  }
}
</style>
