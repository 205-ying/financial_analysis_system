<template>
  <div class="expenses-container">
    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" :inline="true" label-width="80px">
        <el-form-item label="门店">
          <el-select
            v-model="queryForm.store_id"
            placeholder="请选择门店"
            clearable
            style="width: 200px"
          >
            <el-option label="全部门店" :value="undefined" />
            <el-option
              v-for="store in storeList"
              :key="store.id"
              :label="store.name"
              :value="store.id"
            />
          </el-select>
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
            type="success"
            :icon="Plus"
            v-permission="'expense:create'"
            @click="handleCreate"
          >
            新增费用
          </el-button>
          <el-button
            type="warning"
            :icon="Download"
            v-permission="'expense:export'"
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
        :data="tableData"
        stripe
        border
        v-loading="loading"
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
              type="primary"
              size="small"
              link
              :icon="Edit"
              v-permission="'expense:update'"
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-button
              type="danger"
              size="small"
              link
              :icon="Delete"
              v-permission="'expense:delete'"
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Plus, Download, View, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAllStores } from '@/api/store'
import { getExpenseTypeList, getExpenseRecordList } from '@/api/expense'
import type { StoreInfo, ExpenseTypeInfo, ExpenseRecordInfo, ExpenseRecordQuery } from '@/types'
import dayjs from 'dayjs'

// 门店列表
const storeList = ref<StoreInfo[]>([])

// 费用类型列表
const expenseTypeList = ref<ExpenseTypeInfo[]>([])

// 表格数据
const tableData = ref<ExpenseRecordInfo[]>([])
const loading = ref(false)
const total = ref(0)

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

/**
 * 格式化数字
 */
const formatNumber = (value: number): string => {
  if (value === 0) return '0.00'
  if (!value) return '0.00'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/**
 * 格式化日期时间
 */
const formatDateTime = (value: string): string => {
  return dayjs(value).format('YYYY-MM-DD HH:mm:ss')
}

/**
 * 加载门店列表
 */
const loadStores = async () => {
  try {
    const { data } = await getAllStores()
    storeList.value = data
  } catch (error) {
    console.error('加载门店列表失败:', error)
  }
}

/**
 * 加载费用类型列表
 */
const loadExpenseTypes = async () => {
  try {
    const { data } = await getExpenseTypeList()
    expenseTypeList.value = data
  } catch (error) {
    console.error('加载费用类型列表失败:', error)
  }
}

/**
 * 加载表格数据
 */
const loadTableData = async () => {
  try {
    loading.value = true
    const { data } = await getExpenseRecordList(queryForm)
    tableData.value = data.items
    total.value = data.total
  } catch (error) {
    console.error('加载费用记录列表失败:', error)
  } finally {
    loading.value = false
  }
}

/**
 * 处理查询
 */
const handleQuery = () => {
  if (dateRange.value) {
    queryForm.start_date = dateRange.value[0]
    queryForm.end_date = dateRange.value[1]
  } else {
    queryForm.start_date = undefined
    queryForm.end_date = undefined
  }
  queryForm.page = 1
  loadTableData()
}

/**
 * 处理重置
 */
const handleReset = () => {
  queryForm.store_id = undefined
  queryForm.expense_type_id = undefined
  queryForm.start_date = undefined
  queryForm.end_date = undefined
  queryForm.page = 1
  queryForm.page_size = 20
  dateRange.value = undefined
  loadTableData()
}

/**
 * 处理新增
 */
const handleCreate = () => {
  ElMessage.info('新增费用功能待实现')
}

/**
 * 处理导出
 */
const handleExport = () => {
  ElMessage.info('导出功能待实现')
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
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

onMounted(() => {
  loadStores()
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
