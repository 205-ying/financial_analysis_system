/**
 * 数据导入相关接口
 */
import request from '@/utils/request'
import type {
  ApiResponse,
  PageData,
  ImportJob,
  ImportJobDetail,
  ImportJobError,
  ImportJobQuery,
  ImportJobErrorQuery,
  ImportTargetType
} from '@/types'

/**
 * 创建导入任务（上传文件）
 */
export function createImportJob(formData: FormData): Promise<ApiResponse<ImportJob>> {
  return request.post('/import-jobs', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

/**
 * 执行导入任务
 */
export function runImportJob(id: number): Promise<ApiResponse<ImportJob>> {
  return request.post(`/import-jobs/${id}/run`)
}

/**
 * 获取导入任务列表
 */
export function getImportJobList(params: ImportJobQuery): Promise<ApiResponse<PageData<ImportJob>>> {
  return request.get('/import-jobs', { params })
}

/**
 * 获取导入任务详情
 */
export function getImportJobDetail(id: number): Promise<ApiResponse<ImportJobDetail>> {
  return request.get(`/import-jobs/${id}`)
}

/**
 * 获取导入任务错误列表
 */
export function getImportJobErrors(
  id: number,
  params: ImportJobErrorQuery
): Promise<ApiResponse<PageData<ImportJobError>>> {
  return request.get(`/import-jobs/${id}/errors`, { params })
}

/**
 * 下载错误报告
 */
export async function downloadErrorReport(id: number, filename: string): Promise<void> {
  try {
    const response = await request.get(`/import-jobs/${id}/error-report`, {
      responseType: 'blob'
    })

    // 创建 Blob URL
    const blob = new Blob([response], { type: 'text/csv;charset=utf-8' })
    const url = window.URL.createObjectURL(blob)

    // 创建下载链接并触发下载
    const link = document.createElement('a')
    link.href = url
    link.download = filename || `error_report_${id}.csv`
    document.body.appendChild(link)
    link.click()

    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('下载错误报告失败：', error)
    throw error
  }
}
