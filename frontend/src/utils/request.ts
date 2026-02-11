/**
 * Axios 封装 - 请求/响应拦截器
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { envConfig, REQUEST_TIMEOUT } from '@/config'

// 创建 axios 实例
const service: AxiosInstance = axios.create({
  baseURL: envConfig.apiBaseUrl,
  timeout: REQUEST_TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
service.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    const authStore = useAuthStore()
    
    // 自动添加 Authorization header
    if (authStore.token && config.headers) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    
    return config
  },
  (error: AxiosError) => {
    console.error('请求错误：', error)
    return Promise.reject(error)
  }
)

// 标记是否正在处理401错误，避免重复处理
let isRefreshing = false

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    const res = response.data
    
    // 统一响应格式处理
    // 后端成功返回的 code 是 200，不是 0
    if (res.code !== undefined && res.code !== 200 && res.code !== 0) {
      // 业务错误
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    // 返回整个响应对象（包含 code, message, data）
    return res
  },
  (error: AxiosError) => {
    console.error('响应错误：', error.message || error)
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // 未授权 - 静默清除token，让路由守卫统一处理跳转和提示
          if (!isRefreshing) {
            isRefreshing = true
            const authStore = useAuthStore()
            authStore.logout(true) // 静默登出：只清除数据，不跳转
            // 延迟重置标记，避免并发请求重复处理
            setTimeout(() => {
              isRefreshing = false
            }, 1000)
          }
          break
          
        case 403:
          // 无权限 - 仅提示，不跳转页面
          ElMessage.error('无权限执行此操作')
          break
          
        case 404:
          ElMessage.error('请求的资源不存在')
          break
          
        case 500:
          ElMessage.error('服务器错误，请稍后重试')
          break
          
        case 504:
          // 网关超时
          ElMessage.error('请求超时，请缩小查询范围或稍后重试')
          break
          
        default: {
          // 其他错误
          const message = (data as any)?.detail || (data as any)?.message || '请求失败'
          ElMessage.error(message)
          break
        }
      }
    } else if (error.code === 'ECONNABORTED') {
      // 请求超时
      ElMessage.error('请求超时，请缩小查询范围或稍后重试')
    } else if (error.request) {
      // 请求已发送但没有收到响应
      ElMessage.error('网络错误，请检查网络连接')
    } else {
      // 其他错误
      ElMessage.error(error.message || '请求失败')
    }
    
    return Promise.reject(error)
  }
)

export default service
