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

// 权限码常量（单一数据源）
export const PERMISSIONS = {
  SUPER_ADMIN: '*:*:*',
  DASHBOARD_VIEW: 'dashboard:view',
  ORDER_VIEW: 'order:view',
  ORDER_CREATE: 'order:create',
  ORDER_UPDATE: 'order:update',
  ORDER_DELETE: 'order:delete',
  ORDER_EXPORT: 'order:export',
  EXPENSE_VIEW: 'expense:view',
  EXPENSE_CREATE: 'expense:create',
  EXPENSE_UPDATE: 'expense:update',
  EXPENSE_DELETE: 'expense:delete',
  EXPENSE_EXPORT: 'expense:export',
  BUDGET_VIEW: 'budget:view',
  BUDGET_MANAGE: 'budget:manage',
  CVP_VIEW: 'decision:cvp',
  KPI_VIEW: 'kpi:view',
  KPI_REBUILD: 'kpi:rebuild',
  REPORT_VIEW: 'report:view',
  REPORT_EXPORT: 'report:export',
  AUDIT_VIEW: 'audit:view',
  IMPORT_JOB_CREATE: 'import_job:create',
  IMPORT_JOB_VIEW: 'import_job:view',
  IMPORT_JOB_RUN: 'import_job:run',
  IMPORT_JOB_DOWNLOAD: 'import_job:download',
  PRODUCT_ANALYSIS_VIEW: 'product_analysis:view',
  USER_VIEW: 'user:view',
  USER_CREATE: 'user:create',
  USER_EDIT: 'user:edit',
  ROLE_VIEW: 'role:view',
  ROLE_CREATE: 'role:create',
  ROLE_EDIT: 'role:edit',
  ROLE_DELETE: 'role:delete',
  ROLE_ASSIGN_PERMISSION: 'role:assign-permission',
  ROLE_ASSIGN_USER: 'role:assign-permission',
} as const
