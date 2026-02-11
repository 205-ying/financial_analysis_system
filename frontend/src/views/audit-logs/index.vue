<template>
  <div class="audit-logs-container">
    <!-- 筛选条件 -->
    <el-card class="filter-card" shadow="never">
      <el-form :model="queryForm" :inline="true" label-width="80px">
        <el-form-item label="用户名">
          <el-input
            v-model="queryForm.username"
            placeholder="请输入用户名"
            clearable
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="操作类型">
          <el-select
            v-model="queryForm.action"
            placeholder="请选择操作类型"
            clearable
            style="width: 200px"
          >
            <el-option label="全部" :value="undefined" />
            <el-option
              v-for="action in actionList"
              :key="action"
              :label="getActionLabel(action)"
              :value="action"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="资源类型">
          <el-select
            v-model="queryForm.resource_type"
            placeholder="请选择资源类型"
            clearable
            style="width: 200px"
          >
            <el-option label="全部" :value="undefined" />
            <el-option
              v-for="type in resourceTypeList"
              :key="type"
              :label="getResourceTypeLabel(type)"
              :value="type"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="queryForm.status"
            placeholder="请选择状态"
            clearable
            style="width: 150px"
          >
            <el-option label="全部" :value="undefined" />
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failure" />
            <el-option label="错误" value="error" />
          </el-select>
        </el-form-item>

        <el-form-item label="日期范围">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="-"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 400px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
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
        
        <el-table-column prop="username" label="用户" width="120" />
        
        <el-table-column prop="action" label="操作类型" width="150">
          <template #default="{ row }">
            <el-tag :type="getActionTagType(row.action)" size="small">
              {{ getActionLabel(row.action) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="resource_type" label="资源类型" width="120">
          <template #default="{ row }">
            <span v-if="row.resource_type">{{ getResourceTypeLabel(row.resource_type) }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="resource_id" label="资源ID" width="100" align="center">
          <template #default="{ row }">
            <span v-if="row.resource_id">{{ row.resource_id }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        
        <el-table-column prop="created_at" label="操作时间" width="180" align="center">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="100" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              :icon="View"
              @click="handleViewDetail(row)"
            >
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleQuery"
          @current-change="handleQuery"
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="审计日志详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="currentLog" class="detail-content">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="日志ID">{{ currentLog.id }}</el-descriptions-item>
          <el-descriptions-item label="用户">{{ currentLog.username }}</el-descriptions-item>
          <el-descriptions-item label="操作类型">
            <el-tag :type="getActionTagType(currentLog.action)" size="small">
              {{ getActionLabel(currentLog.action) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentLog.status)" size="small">
              {{ getStatusLabel(currentLog.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="资源类型">
            {{ currentLog.resource_type ? getResourceTypeLabel(currentLog.resource_type) : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="资源ID">
            {{ currentLog.resource_id || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="IP地址">
            {{ currentLog.ip_address || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="操作时间">
            {{ formatDateTime(currentLog.created_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider>User-Agent</el-divider>
        <div class="user-agent">
          {{ currentLog.user_agent || '-' }}
        </div>

        <el-divider v-if="currentLog.error_message">错误信息</el-divider>
        <el-alert
          v-if="currentLog.error_message"
          :title="currentLog.error_message"
          type="error"
          :closable="false"
        />

        <el-divider>操作详情</el-divider>
        <div class="detail-json">
          <pre v-if="currentLog.detail">{{ formatJSON(currentLog.detail) }}</pre>
          <div v-else class="text-muted">无详情信息</div>
        </div>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Refresh, View } from '@element-plus/icons-vue'
import { 
  getAuditLogs, 
  getAuditActions, 
  getResourceTypes,
  type AuditLog,
  type AuditLogQuery 
} from '@/api/audit'

// 查询表单
const queryForm = reactive<AuditLogQuery>({
  page: 1,
  page_size: 20,
  username: undefined,
  action: undefined,
  resource_type: undefined,
  status: undefined,
  start_date: undefined,
  end_date: undefined
})

// 日期范围
const dateRange = ref<[string, string] | null>(null)

// 分页信息
const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
  total_pages: 0
})

// 表格数据
const tableData = ref<AuditLog[]>([])
const loading = ref(false)

// 操作类型和资源类型列表
const actionList = ref<string[]>([])
const resourceTypeList = ref<string[]>([])

// 详情弹窗
const detailDialogVisible = ref(false)
const currentLog = ref<AuditLog | null>(null)

/**
 * 查询数据
 */
const handleQuery = async () => {
  loading.value = true
  
  try {
    // 处理日期范围
    if (dateRange.value && dateRange.value.length === 2) {
      queryForm.start_date = dateRange.value[0]
      queryForm.end_date = dateRange.value[1]
    } else {
      queryForm.start_date = undefined
      queryForm.end_date = undefined
    }
    
    queryForm.page = pagination.page
    queryForm.page_size = pagination.page_size
    
    const res = await getAuditLogs(queryForm)
    
    // 从响应中提取数据（res.data 包含实际数据）
    const data = res.data || res
    tableData.value = data.items || []
    pagination.total = data.total || 0
    pagination.total_pages = data.total_pages || 0
    pagination.page = data.page || 1
    pagination.page_size = data.page_size || 20
  } catch (error: any) {
    ElMessage.error(error.message || '查询失败')
  } finally {
    loading.value = false
  }
}

/**
 * 重置查询
 */
const handleReset = () => {
  queryForm.username = undefined
  queryForm.action = undefined
  queryForm.resource_type = undefined
  queryForm.status = undefined
  dateRange.value = null
  pagination.page = 1
  handleQuery()
}

/**
 * 查看详情
 */
const handleViewDetail = (row: AuditLog) => {
  currentLog.value = row
  detailDialogVisible.value = true
}

/**
 * 获取操作类型标签
 */
const getActionLabel = (action: string): string => {
  const labels: Record<string, string> = {
    'login': '登录',
    'logout': '登出',
    'login_failed': '登录失败',
    'CREATE_EXPENSE': '创建费用',
    'UPDATE_EXPENSE': '更新费用',
    'DELETE_EXPENSE': '删除费用',
    'REBUILD_KPI': '重建KPI',
    'create_order': '创建订单',
    'update_order': '更新订单',
    'delete_order': '删除订单'
  }
  return labels[action] || action
}

/**
 * 获取操作类型标签类型
 */
const getActionTagType = (action: string): 'success' | 'info' | 'warning' | 'danger' => {
  if (action.includes('delete') || action.includes('DELETE')) return 'danger'
  if (action.includes('create') || action.includes('CREATE')) return 'success'
  if (action.includes('update') || action.includes('UPDATE')) return 'warning'
  if (action === 'login') return 'success'
  if (action.includes('failed') || action.includes('FAILED')) return 'danger'
  return 'info'
}

/**
 * 获取资源类型标签
 */
const getResourceTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    'user': '用户',
    'expense': '费用',
    'kpi': 'KPI',
    'order': '订单',
    'store': '门店',
    'product': '商品'
  }
  return labels[type] || type
}

/**
 * 获取状态标签
 */
const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    'success': '成功',
    'failure': '失败',
    'error': '错误'
  }
  return labels[status] || status
}

/**
 * 获取状态标签类型
 */
const getStatusTagType = (status: string): 'success' | 'warning' | 'danger' => {
  if (status === 'success') return 'success'
  if (status === 'failure') return 'warning'
  return 'danger'
}

/**
 * 格式化日期时间
 */
const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day} ${hour}:${minute}:${second}`
}

/**
 * 格式化JSON
 */
const formatJSON = (jsonStr: string): string => {
  try {
    const obj = JSON.parse(jsonStr)
    return JSON.stringify(obj, null, 2)
  } catch {
    return jsonStr
  }
}

/**
 * 加载操作类型和资源类型
 */
const loadOptions = async () => {
  try {
    const [actions, resourceTypes] = await Promise.all([
      getAuditActions(),
      getResourceTypes()
    ])
    actionList.value = actions
    resourceTypeList.value = resourceTypes
  } catch (error: any) {
    console.error('加载选项失败:', error)
  }
}

/**
 * 初始化
 */
onMounted(() => {
  loadOptions()
  handleQuery()
})
</script>

<style scoped lang="scss">
.audit-logs-container {
  .filter-card {
    margin-bottom: 20px;
  }

  .pagination-container {
    margin-top: 20px;
    display: flex;
    justify-content: center;
  }

  .text-muted {
    color: #909399;
  }

  .detail-content {
    .user-agent {
      padding: 10px;
      background-color: #f5f7fa;
      border-radius: 4px;
      word-break: break-all;
      font-size: 14px;
      color: #606266;
    }

    .detail-json {
      max-height: 400px;
      overflow-y: auto;
      background-color: #f5f7fa;
      border-radius: 4px;
      padding: 15px;

      pre {
        margin: 0;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
        color: #303133;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }
  }
}
</style>
