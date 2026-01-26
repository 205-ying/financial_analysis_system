/**
 * 应用配置常量
 */

// API基础URL
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1'

// 应用信息
export const APP_INFO = {
  name: '餐饮企业财务分析系统',
  version: '1.0.0',
  description: '提供全面的财务数据分析和可视化'
}

// 存储键名
export const STORAGE_KEYS = {
  AUTH: 'auth',
  TOKEN: 'token',
  USER_INFO: 'userInfo',
  PERMISSIONS: 'permissions',
  THEME: 'theme'
}

// 分页配置
export const PAGINATION = {
  PAGE_SIZE: 10,
  PAGE_SIZES: [10, 20, 50, 100]
}

// 日期格式
export const DATE_FORMAT = {
  DEFAULT: 'YYYY-MM-DD',
  DATETIME: 'YYYY-MM-DD HH:mm:ss',
  TIME: 'HH:mm:ss',
  MONTH: 'YYYY-MM',
  YEAR: 'YYYY'
}

// 请求超时时间（毫秒）
// 报表查询可能涉及大量数据聚合，设置为60秒
export const REQUEST_TIMEOUT = 60000

// Token过期时间（毫秒）
export const TOKEN_EXPIRE_TIME = 30 * 60 * 1000 // 30分钟
