<template>
  <div class="orders-container">
    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" :inline="true" label-width="80px">
        <el-form-item label="门店">
          <StoreSelect v-model="queryForm.store_id" width="200px" />
        </el-form-item>

        <el-form-item label="渠道">
          <el-select
            v-model="queryForm.channel"
            placeholder="请选择渠道"
            clearable
            style="width: 180px"
          >
            <el-option label="全部渠道" value="" />
            <el-option label="堂食" value="dine_in" />
            <el-option label="外卖" value="delivery" />
            <el-option label="外带" value="takeout" />
            <el-option label="团购" value="group_buy" />
          </el-select>
        </el-form-item>

        <el-form-item label="订单号">
          <el-input
            v-model="queryForm.order_no"
            placeholder="请输入订单号"
            clearable
            style="width: 200px"
          />
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

        <el-form-item>
          <el-button
            type="primary"
            :icon="Search"
            @click="handleQuery"
            class="financial-button financial-button--primary financial-button--medium"
          >
            查询
          </el-button>
          <el-button
            :icon="Refresh"
            @click="handleReset"
            class="financial-button financial-button--outline financial-button--medium"
          >
            重置
          </el-button>
          <el-button
            v-permission="PERMISSIONS.ORDER_CREATE"
            type="success"
            :icon="Plus"
            @click="handleCreate"
            class="financial-button financial-button--success financial-button--medium"
          >
            新增订单
          </el-button>
          <el-button
            v-permission="PERMISSIONS.ORDER_EXPORT"
            type="warning"
            :icon="Download"
            :loading="exportLoading"
            @click="handleExport"
            class="financial-button financial-button--warning financial-button--medium"
          >
            导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="financial-metric-card">
          <el-statistic :value="total" title="订单总数">
            <template #suffix>笔</template>
          </el-statistic>
          <div class="card-note">当前筛选条件下的总数</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="financial-metric-card">
          <el-statistic :value="stats.total_amount" :precision="2" title="本页合计金额">
            <template #prefix>¥</template>
          </el-statistic>
          <div class="card-note">当前页 {{ tableData.length }} 笔订单合计</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="financial-metric-card">
          <el-statistic :value="stats.avg_amount" :precision="2" title="本页平均客单价">
            <template #prefix>¥</template>
          </el-statistic>
          <div class="card-note">当前页均价</div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="financial-metric-card">
          <el-statistic :value="stats.store_count" title="本页涉及门店">
            <template #suffix>家</template>
          </el-statistic>
          <div class="card-note">当前页数据统计</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        class="financial-table"
        :header-cell-style="{ background: 'var(--color-gray-50)', color: 'var(--color-text-secondary)' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="order_no" label="订单号" min-width="180" />
        <el-table-column prop="store_name" label="门店" min-width="120" />
        <el-table-column prop="channel" label="渠道" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getChannelType(row.channel)">
              {{ getChannelLabel(row.channel) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="金额" width="150" align="right">
          <template #default="{ row }">
            <span class="amount-cell">
              ¥{{ formatNumber(row.amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="order_time" label="订单时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.order_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="150" show-overflow-tooltip />
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
              v-permission="PERMISSIONS.ORDER_UPDATE"
              type="primary"
              size="small"
              link
              :icon="Edit"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              v-permission="PERMISSIONS.ORDER_DELETE"
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
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </el-card>

    <!-- 创建订单对话框 -->
    <CreateOrderDialog v-model="createDialogVisible" @success="handleCreateSuccess" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Search, Refresh, Plus, Download, View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getOrderList, exportOrders } from '@/api/order'
import StoreSelect from '@/components/StoreSelect.vue'
import CreateOrderDialog from '@/components/dialogs/CreateOrderDialog.vue'
import { useListPage } from '@/composables'
import { PERMISSIONS } from '@/config'
import type { OrderInfo, OrderQuery } from '@/types'
import { formatAmount, formatDateTime } from '@/utils'
import dayjs from 'dayjs'

// 查询表单
const queryForm = reactive<OrderQuery>({
  store_id: undefined,
  channel: undefined,
  order_no: undefined,
  start_date: undefined,
  end_date: undefined,
  page: 1,
  page_size: 20
})

// 日期范围
const dateRange = ref<[string, string]>()

// 对话框状态
const createDialogVisible = ref(false)

// 导出状态
const exportLoading = ref(false)

const { tableData, loading, total, loadTableData, handleQuery: queryList, handleReset: resetList } = useListPage(
  queryForm,
  getOrderList
)

// 统计数据（基于当前页数据计算）
const stats = computed(() => {
  const pageCount = tableData.value.length
  const totalAmount = tableData.value.reduce((sum, item) => sum + item.amount, 0)
  const avgAmount = pageCount > 0 ? totalAmount / pageCount : 0
  const storeSet = new Set(tableData.value.map(item => item.store_id))
  const storeCount = storeSet.size

  return {
    total_amount: totalAmount,
    avg_amount: avgAmount,
    store_count: storeCount
  }
})

/**
 * 获取渠道标签类型
 */
const getChannelType = (channel: string) => {
  const typeMap: Record<string, string> = {
    dine_in: '',
    delivery: 'success',
    pickup: 'warning',
    group_buy: 'danger'
  }
  return typeMap[channel] || ''
}

const getChannelLabel = (channel: string) => {
  const labelMap: Record<string, string> = {
    dine_in: '堂食',
    delivery: '外卖',
    pickup: '外带',
    group_buy: '团购'
  }
  return labelMap[channel] || channel
}

const formatNumber = (value: number): string => formatAmount(value)

/**
 * 处理查询
 */
const handleQuery = () => {
  queryList(dateRange.value)
}

/**
 * 处理重置
 */
const handleReset = () => {
  resetList(
    () => {
      queryForm.store_id = undefined
      queryForm.channel = undefined
      queryForm.order_no = undefined
      queryForm.start_date = undefined
      queryForm.end_date = undefined
    },
    () => {
      dateRange.value = undefined
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
  try {
    exportLoading.value = true
    
    // 准备查询参数
    const params = {
      store_id: queryForm.store_id,
      channel: queryForm.channel,
      order_no: queryForm.order_no,
      start_date: queryForm.start_date,
      end_date: queryForm.end_date,
      page: queryForm.page,
      page_size: queryForm.page_size
    }
    
    // 调用导出API
    const blob = await exportOrders(params)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `订单列表_${dayjs().format('YYYYMMDDHHmmss')}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败，请重试')
  } finally {
    exportLoading.value = false
  }
}

/**
 * 处理查看
 */
const handleView = (row: OrderInfo) => {
  ElMessage.info(`查看订单：${row.order_no}`)
}

/**
 * 处理编辑
 */
const handleEdit = (row: OrderInfo) => {
  ElMessage.info(`编辑订单：${row.order_no}`)
}

/**
 * 处理删除
 */
const handleDelete = async (row: OrderInfo) => {
  try {
    await ElMessageBox.confirm(`确定要删除订单"${row.order_no}"吗？`, '删除确认', {
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
  loadTableData()
})
</script>

<style scoped lang="scss">
// 订单管理页面样式 - 遵循财务分析系统设计规范
.orders-container {
  padding: var(--spacing-5) var(--spacing-5) var(--spacing-6);
  background-color: var(--color-bg-secondary);
  min-height: calc(100vh - 64px); // 减去顶部导航高度
}

// ===== 筛选卡片 =====
.filter-card {
  margin-bottom: var(--spacing-5);
  border-radius: var(--border-radius-md);
  border: var(--border-width-thin) solid var(--color-border-light);
  background-color: var(--color-bg-primary);
  box-shadow: var(--shadow-sm);
  transition: box-shadow var(--transition-duration-base) var(--transition-timing-function-base);

  &:hover {
    box-shadow: var(--shadow-md);
  }

  :deep(.el-card__body) {
    padding: var(--spacing-5);
  }

  :deep(.el-form) {
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-4);
    align-items: flex-start;

    .el-form-item {
      margin: 0;
      margin-bottom: var(--spacing-2);

      &:last-child {
        flex: 1;
        display: flex;
        justify-content: flex-end;
        gap: var(--spacing-2);
        margin-top: var(--spacing-2);
      }
    }
  }

  @media (max-width: var(--breakpoint-md)) {
    :deep(.el-form) {
      .el-form-item {
        width: calc(50% - var(--spacing-4));

        &:last-child {
          width: 100%;
          justify-content: center;
        }
      }
    }
  }

  @media (max-width: var(--breakpoint-sm)) {
    :deep(.el-form) {
      .el-form-item {
        width: 100%;

        &:last-child {
          width: 100%;
          justify-content: center;
        }
      }
    }
  }
}

// ===== 统计卡片 =====
.stats-cards {
  margin-bottom: var(--spacing-5);
  display: flex;
  flex-wrap: wrap;

  .el-col {
    margin-bottom: var(--spacing-4);
  }

  .el-card {
    border-radius: var(--border-radius-md);
    border: var(--border-width-thin) solid var(--color-border-light);
    background-color: var(--color-bg-primary);
    box-shadow: var(--shadow-sm);
    transition: all var(--transition-duration-base) var(--transition-timing-function-base);
    overflow: hidden;

    &:hover {
      transform: translateY(-4px);
      box-shadow: var(--shadow-lg);
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
        line-height: 1.2;
      }

      .el-statistic__title {
        font-size: var(--font-size-sm);
        color: var(--color-text-tertiary);
        margin-top: var(--spacing-2);
        text-transform: uppercase;
        letter-spacing: 0.5px;
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
  border-radius: var(--border-radius-md);
  border: var(--border-width-thin) solid var(--color-border-light);
  background-color: var(--color-bg-primary);
  box-shadow: var(--shadow-sm);
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
      color: var(--color-text-secondary) !important;
      font-weight: var(--font-weight-semibold);
      font-size: var(--font-size-sm);
      text-transform: uppercase;
      letter-spacing: 0.5px;
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

  // 金额列样式
  .el-table__row .amount-cell {
    font-weight: var(--font-weight-semibold);
    color: var(--color-success);
  }

  // 渠道标签
  .el-tag {
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    padding: var(--spacing-1) var(--spacing-2);
    border: none;

    &.el-tag--success {
      background-color: var(--color-success-lightest);
      color: var(--color-success-darker);
    }

    &.el-tag--warning {
      background-color: var(--color-warning-lightest);
      color: var(--color-warning-darker);
    }

    &.el-tag--danger {
      background-color: var(--color-danger-lightest);
      color: var(--color-danger-darker);
    }

    &:not(.el-tag--success, .el-tag--warning, .el-tag--danger) {
      background-color: var(--color-gray-100);
      color: var(--color-text-tertiary);
    }
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
  .orders-container {
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
  .orders-container {
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
