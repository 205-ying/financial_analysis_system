<template>
  <div class="import-job-detail-container">
    <!-- 加载中 -->
    <el-skeleton v-if="loading" :rows="10" animated />

    <template v-else-if="jobDetail">
      <!-- 头部信息 -->
      <el-card class="header-card" shadow="never">
        <div class="header-content">
          <div class="title-section">
            <h2>{{ jobDetail.filename }}</h2>
            <el-tag :type="ImportJobStatusMap[jobDetail.status].type" size="large">
              {{ ImportJobStatusMap[jobDetail.status].text }}
            </el-tag>
          </div>
          <div class="action-section">
            <el-button
              v-if="jobDetail.status === ImportJobStatus.PENDING || jobDetail.status === ImportJobStatus.FAIL"
              v-permission="PERMISSIONS.IMPORT_JOB_RUN"
              type="primary"
              :icon="VideoPlay"
              :loading="running"
              @click="handleRun"
            >
              运行任务
            </el-button>
            <el-button
              v-if="jobDetail.fail_rows > 0"
              v-permission="PERMISSIONS.IMPORT_JOB_DOWNLOAD"
              type="warning"
              :icon="Download"
              @click="handleDownload"
            >
              下载错误报告
            </el-button>
            <el-button :icon="Refresh" @click="handleRefresh">刷新</el-button>
            <el-button @click="handleBack">返回</el-button>
          </div>
        </div>
      </el-card>

      <!-- 统计卡片 -->
      <el-row :gutter="20" class="stats-row">
        <el-col :span="6">
          <el-card shadow="hover" class="stats-card">
            <el-statistic title="导入类型" :value="ImportTargetTypeMap[jobDetail.target_type]" />
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stats-card total">
            <el-statistic title="总行数" :value="jobDetail.total_rows">
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stats-card success">
            <el-statistic title="成功行数" :value="jobDetail.success_rows">
              <template #prefix>
                <el-icon><CircleCheck /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stats-card fail">
            <el-statistic title="失败行数" :value="jobDetail.fail_rows">
              <template #prefix>
                <el-icon><CircleClose /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>

      <!-- 基本信息 -->
      <el-card class="info-card" shadow="never">
        <template #header>
          <span class="card-title">基本信息</span>
        </template>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="任务ID">{{ jobDetail.id }}</el-descriptions-item>
          <el-descriptions-item label="文件名">{{ jobDetail.filename }}</el-descriptions-item>
          <el-descriptions-item label="文件类型">
            {{ ImportSourceTypeMap[jobDetail.source_type] }}
          </el-descriptions-item>
          <el-descriptions-item label="门店">
            {{ jobDetail.store_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建人">
            {{ jobDetail.created_by?.real_name || jobDetail.created_by?.username || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(jobDetail.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatDateTime(jobDetail.started_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatDateTime(jobDetail.finished_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <!-- 错误列表 -->
      <el-card v-if="jobDetail.fail_rows > 0" class="error-card" shadow="never">
        <template #header>
          <span class="card-title">错误详情（共 {{ errorTotal }} 条）</span>
        </template>

        <el-table v-loading="errorLoading" :data="errorList" border stripe>
          <el-table-column prop="row_number" label="行号" width="100" align="center" />
          <el-table-column prop="error_type" label="错误类型" width="150" />
          <el-table-column prop="error_message" label="错误信息" min-width="300" show-overflow-tooltip />
          <el-table-column label="原始数据" min-width="200">
            <template #default="{ row }">
              <el-popover placement="left" :width="400" trigger="click">
                <template #reference>
                  <el-button link type="primary" size="small">查看</el-button>
                </template>
                <el-scrollbar max-height="400px">
                  <pre class="raw-data">{{ JSON.stringify(row.raw_data, null, 2) }}</pre>
                </el-scrollbar>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="记录时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>

        <!-- 错误列表分页 -->
        <el-pagination
          v-model:current-page="errorQuery.page"
          v-model:page-size="errorQuery.page_size"
          :total="errorTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadErrors"
          @current-change="loadErrors"
        />
      </el-card>

      <!-- 无错误提示 -->
      <el-card v-else class="no-error-card" shadow="never">
        <el-empty description="暂无错误记录">
          <template #image>
            <el-icon :size="100" color="var(--el-color-success)">
              <CircleCheck />
            </el-icon>
          </template>
        </el-empty>
      </el-card>
    </template>

    <!-- 未找到任务 -->
    <el-empty v-else description="未找到该导入任务" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  VideoPlay,
  Download,
  Refresh,
  Document,
  CircleCheck,
  CircleClose
} from '@element-plus/icons-vue'
import {
  getImportJobDetail,
  getImportJobErrors,
  runImportJob,
  downloadErrorReport
} from '@/api/import_jobs'
import {
  ImportTargetTypeMap,
  ImportSourceTypeMap,
  ImportJobStatusMap,
  ImportJobStatus,
  type ImportJobDetail,
  type ImportJobError,
  type ImportJobErrorQuery
} from '@/types'
import { PERMISSIONS } from '@/config'

const route = useRoute()
const router = useRouter()

// 任务ID
const jobId = computed(() => Number(route.params.id))

// 任务详情
const loading = ref(false)
const jobDetail = ref<ImportJobDetail | null>(null)

// 错误列表
const errorLoading = ref(false)
const errorList = ref<ImportJobError[]>([])
const errorTotal = ref(0)
const errorQuery = reactive<ImportJobErrorQuery>({
  page: 1,
  page_size: 20
})

// 运行状态
const running = ref(false)

// 格式化日期时间
const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载任务详情
const loadDetail = async () => {
  loading.value = true
  try {
    const response = await getImportJobDetail(jobId.value)
    jobDetail.value = response.data

    // 如果有失败行，加载错误列表
    if (jobDetail.value.fail_rows > 0) {
      await loadErrors()
    }
  } catch {
    ElMessage.error('加载详情失败')
  } finally {
    loading.value = false
  }
}

// 加载错误列表
const loadErrors = async () => {
  errorLoading.value = true
  try {
    const response = await getImportJobErrors(jobId.value, errorQuery)
    errorList.value = response.data.items
    errorTotal.value = response.data.total
  } catch {
    ElMessage.error('加载错误列表失败')
  } finally {
    errorLoading.value = false
  }
}

// 运行任务
const handleRun = async () => {
  try {
    await ElMessageBox.confirm('确定要运行此任务吗？', '提示', {
      type: 'warning'
    })

    running.value = true
    await runImportJob(jobId.value)
    ElMessage.success('任务已开始运行')
    
    // 延迟刷新以显示最新状态
    setTimeout(() => {
      loadDetail()
    }, 1000)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('运行失败')
    }
  } finally {
    running.value = false
  }
}

// 下载错误报告
const handleDownload = async () => {
  try {
    await downloadErrorReport(jobId.value, `error_report_${jobId.value}.csv`)
    ElMessage.success('下载成功')
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 刷新
const handleRefresh = () => {
  loadDetail()
}

// 返回
const handleBack = () => {
  router.back()
}

// 页面加载
onMounted(() => {
  loadDetail()
})
</script>

<style scoped lang="scss">
.import-job-detail-container {
  padding: 20px;

  .header-card {
    margin-bottom: 20px;

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .title-section {
        display: flex;
        align-items: center;
        gap: 15px;

        h2 {
          margin: 0;
          font-size: 20px;
          font-weight: 600;
        }
      }

      .action-section {
        display: flex;
        gap: 10px;
      }
    }
  }

  .stats-row {
    margin-bottom: 20px;

    .stats-card {
      :deep(.el-statistic__content) {
        font-size: 28px;
        font-weight: bold;
      }

      &.total {
        :deep(.el-statistic__content) {
          color: var(--el-color-primary);
        }
      }

      &.success {
        :deep(.el-statistic__content) {
          color: var(--el-color-success);
        }
      }

      &.fail {
        :deep(.el-statistic__content) {
          color: var(--el-color-danger);
        }
      }
    }
  }

  .info-card,
  .error-card,
  .no-error-card {
    margin-bottom: 20px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
    }
  }

  .error-card {
    :deep(.el-pagination) {
      margin-top: 20px;
      justify-content: flex-end;
    }

    .raw-data {
      font-family: 'Courier New', monospace;
      font-size: 12px;
      background: var(--el-fill-color-light);
      padding: 10px;
      border-radius: 4px;
      margin: 0;
    }
  }

  .no-error-card {
    text-align: center;
    padding: 40px 0;
  }
}
</style>
