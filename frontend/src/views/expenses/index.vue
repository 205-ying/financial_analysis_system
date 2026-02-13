<template>
  <div class="expenses-container">
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
            <el-option label="全部类型" :value="undefined" />
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

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
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
        </el-form-item>
      </el-form>
    </el-card>

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
        <el-table-column prop="store_name" label="门店" min-width="120" />
        <el-table-column prop="expense_type_name" label="费用类型" min-width="120" />
        <el-table-column prop="amount" label="金额" width="150" align="right">
          <template #default="{ row }">
            <span style="color: #e6a23c; font-weight: 600">
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
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </el-card>

    <!-- 创建费用对话框 -->
    <CreateExpenseDialog v-model="createDialogVisible" @success="handleCreateSuccess" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Plus, Download, View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import StoreSelect from '@/components/StoreSelect.vue'
import CreateExpenseDialog from '@/components/dialogs/CreateExpenseDialog.vue'
import { getExpenseTypeList, getExpenseRecordList, exportExpenseRecords } from '@/api/expense'
import { useListPage } from '@/composables'
import { PERMISSIONS } from '@/config'
import type { ExpenseTypeInfo, ExpenseRecordInfo, ExpenseRecordQuery } from '@/types'
import { formatAmount, formatDateTime } from '@/utils'
import dayjs from 'dayjs'

// 费用类型列表
const expenseTypeList = ref<ExpenseTypeInfo[]>([])

// 查询表单
const queryForm = reactive<ExpenseRecordQuery>({
  store_id: undefined,
  expense_type_id: undefined,
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

const { tableData, loading, total, loadTableData, handleQuery: queryList, handleReset: resetList } = useListPage<
  ExpenseRecordInfo,
  ExpenseRecordQuery
>(queryForm, getExpenseRecordList)

const formatNumber = (value: number): string => formatAmount(value)

/**
 * 加载费用类型列表
 */
const loadExpenseTypes = async () => {
  try {
    const { data } = await getExpenseTypeList()
    expenseTypeList.value = data
  } catch {
    // 静默失败：避免在控制台输出
  }
}

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
      queryForm.expense_type_id = undefined
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
      expense_type_id: queryForm.expense_type_id,
      start_date: queryForm.start_date,
      end_date: queryForm.end_date,
      page: queryForm.page,
      page_size: queryForm.page_size
    }
    
    // 调用导出API
    const blob = await exportExpenseRecords(params)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `费用记录_${dayjs().format('YYYYMMDDHHmmss')}.xlsx`
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
.expenses-container {
  padding: 0;
}

.filter-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
}
</style>
