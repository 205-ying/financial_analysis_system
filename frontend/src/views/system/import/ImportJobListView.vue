<template>
  <div class="import-job-list-container">
    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="queryParams" @submit.prevent="handleQuery">
        <el-form-item label="导入类型">
          <el-select
            v-model="queryParams.target_type"
            placeholder="全部类型"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="(label, value) in ImportTargetTypeMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="任务状态">
          <el-select
            v-model="queryParams.status"
            placeholder="全部状态"
            clearable
            style="width: 150px"
          >
            <el-option
              v-for="(item, key) in ImportJobStatusMap"
              :key="key"
              :label="item.text"
              :value="key"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="创建日期">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 240px"
          />
        </el-form-item>

        <el-form-item label="关键词">
          <el-input
            v-model="queryParams.keyword"
            placeholder="文件名"
            clearable
            style="width: 200px"
            @keyup.enter="handleQuery"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button
            v-permission="'import_job:create'"
            type="success"
            :icon="Upload"
            @click="handleCreate"
          >
            导入数据
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card" shadow="never">
      <el-table v-loading="loading" :data="tableData" border stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
        <el-table-column prop="target_type" label="导入类型" width="120">
          <template #default="{ row }">
            {{ ImportTargetTypeMap[row.target_type] }}
          </template>
        </el-table-column>
        <el-table-column prop="store_name" label="门店" width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="ImportJobStatusMap[row.status].type">
              {{ ImportJobStatusMap[row.status].text }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_rows" label="总行数" width="100" align="right" />
        <el-table-column prop="success_rows" label="成功" width="100" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-success': row.success_rows > 0 }">
              {{ row.success_rows }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="fail_rows" label="失败" width="100" align="right">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.fail_rows > 0 }">
              {{ row.fail_rows }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="创建人" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              v-permission="'import_job:view'"
              link
              type="primary"
              size="small"
              @click="handleDetail(row)"
            >
              详情
            </el-button>
            <el-button
              v-if="row.status === ImportJobStatus.PENDING || row.status === ImportJobStatus.FAIL"
              v-permission="'import_job:run'"
              link
              type="success"
              size="small"
              @click="handleRun(row)"
            >
              运行
            </el-button>
            <el-button
              v-if="row.fail_rows > 0"
              v-permission="'import_job:download'"
              link
              type="warning"
              size="small"
              @click="handleDownload(row)"
            >
              错误报告
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.page_size"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleQuery"
        @current-change="handleQuery"
      />
    </el-card>

    <!-- 创建任务对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="导入数据"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form ref="createFormRef" :model="createForm" :rules="createRules" label-width="100px">
        <el-form-item label="导入类型" prop="target_type">
          <el-select
            v-model="createForm.target_type"
            placeholder="请选择导入类型"
            style="width: 100%"
          >
            <el-option
              v-for="(label, value) in ImportTargetTypeMap"
              :key="value"
              :label="label"
              :value="value"
            />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="createForm.target_type === ImportTargetType.ORDERS || createForm.target_type === ImportTargetType.EXPENSE_RECORDS"
          label="门店"
          prop="store_id"
        >
          <StoreSelect v-model="createForm.store_id" width="100%" />
        </el-form-item>

        <el-form-item label="文件" prop="file">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-exceed="handleExceed"
            accept=".xlsx,.xls,.csv"
            drag
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              拖拽文件到此处或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                支持 Excel (.xlsx, .xls) 和 CSV (.csv) 格式，文件大小不超过 50MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="handleSubmit">
          上传并创建
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type UploadInstance } from 'element-plus'
import { Search, Refresh, Upload, UploadFilled } from '@element-plus/icons-vue'
import {
  getImportJobList,
  createImportJob,
  runImportJob,
  downloadErrorReport
} from '@/api/import_jobs'
import StoreSelect from '@/components/StoreSelect.vue'
import {
  ImportTargetTypeMap,
  ImportJobStatusMap,
  ImportJobStatus,
  ImportTargetType,
  type ImportJob,
  type ImportJobQuery
} from '@/types'

const router = useRouter()

// 查询参数
const queryParams = reactive<ImportJobQuery>({
  page: 1,
  page_size: 20
})

// 日期范围
const dateRange = ref<[string, string] | null>(null)

// 表格数据
const loading = ref(false)
const tableData = ref<ImportJob[]>([])
const total = ref(0)

// 创建对话框
const createDialogVisible = ref(false)
const uploading = ref(false)
const createFormRef = ref<FormInstance>()
const uploadRef = ref<UploadInstance>()
const createForm = reactive({
  target_type: undefined as ImportTargetType | undefined,
  store_id: undefined as number | undefined,
  file: null as File | null
})

// 表单验证规则
const createRules = {
  target_type: [{ required: true, message: '请选择导入类型', trigger: 'change' }],
  store_id: [{ required: true, message: '请选择门店', trigger: 'change' }],
  file: [{ required: true, message: '请上传文件', trigger: 'change' }]
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 查询数据
const handleQuery = async () => {
  loading.value = true
  try {
    // 处理日期范围
    if (dateRange.value) {
      queryParams.start_date = dateRange.value[0]
      queryParams.end_date = dateRange.value[1]
    } else {
      delete queryParams.start_date
      delete queryParams.end_date
    }

    const response = await getImportJobList(queryParams)
    // 兼容统一响应格式：{code, message, data: {items, total}}
    const data = response.data || response
    tableData.value = data.items || []
    total.value = data.total || 0
  } catch (error) {
    console.error('查询失败：', error)
    ElMessage.error('查询失败')
  } finally {
    loading.value = false
  }
}

// 重置查询
const handleReset = () => {
  queryParams.target_type = undefined
  queryParams.status = undefined
  queryParams.keyword = undefined
  dateRange.value = null
  queryParams.page = 1
  handleQuery()
}

// 打开创建对话框
const handleCreate = async () => {
  createDialogVisible.value = true
}

// 文件变化
const handleFileChange = (uploadFile: any) => {
  createForm.file = uploadFile.raw
}

// 文件超出限制
const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

// 提交创建
const handleSubmit = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    uploading.value = true
    try {
      // 构建 FormData
      const formData = new FormData()
      formData.append('file', createForm.file!)
      formData.append('target_type', createForm.target_type!)
      if (createForm.store_id) {
        formData.append('store_id', createForm.store_id.toString())
      }

      const response = await createImportJob(formData)
      ElMessage.success('创建成功')
      createDialogVisible.value = false
      handleQuery()

      // 跳转到详情页
      router.push(`/system/import-jobs/${response.data.id}`)
    } catch (error) {
      console.error('创建失败：', error)
      ElMessage.error('创建失败')
    } finally {
      uploading.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  createFormRef.value?.resetFields()
  uploadRef.value?.clearFiles()
  createForm.file = null
}

// 查看详情
const handleDetail = (row: ImportJob) => {
  router.push(`/system/import-jobs/${row.id}`)
}

// 运行任务
const handleRun = async (row: ImportJob) => {
  try {
    await ElMessageBox.confirm(`确定要运行任务"${row.filename}"吗？`, '提示', {
      type: 'warning'
    })

    loading.value = true
    await runImportJob(row.id)
    ElMessage.success('任务已开始运行')
    handleQuery()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('运行失败：', error)
      ElMessage.error('运行失败')
    }
  } finally {
    loading.value = false
  }
}

// 下载错误报告
const handleDownload = async (row: ImportJob) => {
  try {
    await downloadErrorReport(row.id, `error_report_${row.id}.csv`)
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载失败：', error)
    ElMessage.error('下载失败')
  }
}

// 页面加载
onMounted(() => {
  handleQuery()
})
</script>

<style scoped lang="scss">
.import-job-list-container {
  padding: 20px;

  .filter-card {
    margin-bottom: 20px;
  }

  .table-card {
    :deep(.el-pagination) {
      margin-top: 20px;
      justify-content: flex-end;
    }
  }

  .text-success {
    color: var(--el-color-success);
    font-weight: bold;
  }

  .text-danger {
    color: var(--el-color-danger);
    font-weight: bold;
  }
}
</style>
