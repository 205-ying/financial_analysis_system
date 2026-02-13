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
            <el-option label="堂食" value="堂食" />
            <el-option label="外卖" value="外卖" />
            <el-option label="外带" value="外带" />
            <el-option label="团购" value="团购" />
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
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button
            v-permission="PERMISSIONS.ORDER_CREATE"
            type="success"
            :icon="Plus"
            @click="handleCreate"
          >
            新增订单
          </el-button>
          <el-button
            v-permission="PERMISSIONS.ORDER_EXPORT"
            type="warning"
            :icon="Download"
            :loading="exportLoading"
            @click="handleExport"
          >
            导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic :value="stats.total_count" title="订单总数">
            <template #suffix>笔</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic :value="stats.total_amount" :precision="2" title="订单总额">
            <template #prefix>¥</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic :value="stats.avg_amount" :precision="2" title="平均客单价">
            <template #prefix>¥</template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card shadow="hover">
          <el-statistic :value="stats.store_count" title="涉及门店">
            <template #suffix>家</template>
          </el-statistic>
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
        :header-cell-style="{ background: '#f5f7fa', color: '#606266' }"
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
            <span style="color: #67c23a; font-weight: 600">
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

// 统计数据
const stats = computed(() => {
  const totalCount = total.value
  const totalAmount = tableData.value.reduce((sum, item) => sum + item.amount, 0)
  const avgAmount = totalCount > 0 ? totalAmount / totalCount : 0
  const storeSet = new Set(tableData.value.map(item => item.store_id))
  const storeCount = storeSet.size

  return {
    total_count: totalCount,
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
.orders-container {
  padding: 0;
}

.filter-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.stats-cards {
  margin-bottom: 20px;

  .el-card {
    :deep(.el-card__body) {
      padding: 20px;
    }
  }
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
