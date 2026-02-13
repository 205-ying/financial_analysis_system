import type { RouteRecordRaw } from 'vue-router'
import { PERMISSIONS } from './constants'

export type DynamicRouteConfig = Omit<RouteRecordRaw, 'component' | 'children'> & {
  component?: () => Promise<unknown>
  meta?: {
    title?: string
    iconKey?: 'DataAnalysis' | 'Document' | 'Money' | 'TrendCharts' | 'List' | 'Upload' | 'Setting' | 'Dish' | 'Wallet'
    hidden?: boolean
    requiresAuth?: boolean
    permissions?: readonly string[]
  }
  children?: DynamicRouteConfig[]
}

export const DYNAMIC_ROUTE_CONFIGS: DynamicRouteConfig[] = [
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/dashboard/index.vue'),
    meta: {
      title: '看板',
      iconKey: 'DataAnalysis',
      requiresAuth: true,
      permissions: [PERMISSIONS.DASHBOARD_VIEW],
    },
  },
  {
    path: '/operations',
    name: 'Operations',
    meta: {
      title: '经营管理',
      iconKey: 'Document',
      requiresAuth: true,
      permissions: [
        PERMISSIONS.ORDER_VIEW,
        PERMISSIONS.EXPENSE_VIEW,
        PERMISSIONS.BUDGET_VIEW,
        PERMISSIONS.BUDGET_MANAGE,
        PERMISSIONS.IMPORT_JOB_VIEW,
      ],
    },
    children: [
      {
        path: '/orders',
        name: 'Orders',
        component: () => import('@/views/orders/index.vue'),
        meta: {
          title: '订单管理',
          iconKey: 'Document',
          requiresAuth: true,
          permissions: [PERMISSIONS.ORDER_VIEW],
        },
      },
      {
        path: '/expenses',
        name: 'Expenses',
        component: () => import('@/views/expenses/index.vue'),
        meta: {
          title: '费用管理',
          iconKey: 'Money',
          requiresAuth: true,
          permissions: [PERMISSIONS.EXPENSE_VIEW],
        },
      },
      {
        path: '/budget',
        name: 'Budget',
        component: () => import('@/views/budget/index.vue'),
        meta: {
          title: '预算管理',
          iconKey: 'Wallet',
          requiresAuth: true,
          permissions: [PERMISSIONS.BUDGET_VIEW, PERMISSIONS.BUDGET_MANAGE],
        },
      },
      {
        path: '/system/import-jobs',
        name: 'ImportJobs',
        component: () => import('@/views/system/import/ImportJobListView.vue'),
        meta: {
          title: '数据导入',
          iconKey: 'Upload',
          requiresAuth: true,
          permissions: [PERMISSIONS.IMPORT_JOB_VIEW],
        },
      },
    ],
  },
  {
    path: '/analysis',
    name: 'Analysis',
    meta: {
      title: '分析中心',
      iconKey: 'TrendCharts',
      requiresAuth: true,
      permissions: [
        PERMISSIONS.KPI_VIEW,
        PERMISSIONS.CVP_VIEW,
        PERMISSIONS.REPORT_VIEW,
        PERMISSIONS.PRODUCT_ANALYSIS_VIEW,
      ],
    },
    children: [
      {
        path: '/kpi',
        name: 'KPI',
        component: () => import('@/views/kpi/index.vue'),
        meta: {
          title: 'KPI 分析',
          iconKey: 'TrendCharts',
          requiresAuth: true,
          permissions: [PERMISSIONS.KPI_VIEW],
        },
      },
      {
        path: '/comparison',
        name: 'Comparison',
        component: () => import('@/views/comparison/index.vue'),
        meta: {
          title: '同比环比分析',
          iconKey: 'TrendCharts',
          requiresAuth: true,
          permissions: [PERMISSIONS.KPI_VIEW],
        },
      },
      {
        path: '/product-analysis',
        name: 'ProductAnalysis',
        component: () => import('@/views/product-analysis/index.vue'),
        meta: {
          title: '菜品分析',
          iconKey: 'Dish',
          requiresAuth: true,
          permissions: [PERMISSIONS.PRODUCT_ANALYSIS_VIEW],
        },
      },
      {
        path: '/decision/cvp',
        name: 'CVP',
        component: () => import('@/views/decision/cvp/index.vue'),
        redirect: '/decision/cvp/dashboard',
        meta: {
          title: '本量利分析',
          iconKey: 'TrendCharts',
          requiresAuth: true,
          permissions: [PERMISSIONS.CVP_VIEW],
        },
        children: [
          {
            path: 'config',
            name: 'CVPConfig',
            component: () => import('@/views/decision/cvp/Config.vue'),
            meta: {
              title: '成本配置',
              requiresAuth: true,
              permissions: [PERMISSIONS.CVP_VIEW],
            },
          },
          {
            path: 'dashboard',
            name: 'CVPDashboard',
            component: () => import('@/views/decision/cvp/Dashboard.vue'),
            meta: {
              title: 'CVP分析',
              requiresAuth: true,
              permissions: [PERMISSIONS.CVP_VIEW],
            },
          },
        ],
      },
      {
        path: '/reports',
        name: 'Reports',
        component: () => import('@/views/analytics/ReportView.vue'),
        meta: {
          title: '报表中心',
          iconKey: 'Document',
          requiresAuth: true,
          permissions: [PERMISSIONS.REPORT_VIEW],
        },
      },
    ],
  },
  {
    path: '/system-management',
    name: 'SystemManagement',
    meta: {
      title: '系统管理',
      iconKey: 'Setting',
      requiresAuth: true,
      permissions: [PERMISSIONS.AUDIT_VIEW, PERMISSIONS.ROLE_VIEW],
    },
    children: [
      {
        path: '/audit-logs',
        name: 'AuditLogs',
        component: () => import('@/views/audit-logs/index.vue'),
        meta: {
          title: '审计日志',
          iconKey: 'List',
          requiresAuth: true,
          permissions: [PERMISSIONS.AUDIT_VIEW],
        },
      },
      {
        path: '/system/roles',
        name: 'Roles',
        component: () => import('@/views/system/roles/index.vue'),
        meta: {
          title: '角色管理',
          iconKey: 'Setting',
          requiresAuth: true,
          permissions: [PERMISSIONS.ROLE_VIEW],
        },
      },
    ],
  },
  {
    path: '/system/import-jobs/:id',
    name: 'ImportJobDetail',
    component: () => import('@/views/system/import/ImportJobDetailView.vue'),
    meta: {
      title: '导入详情',
      hidden: true,
      requiresAuth: true,
      permissions: [PERMISSIONS.IMPORT_JOB_VIEW],
    },
  },
]
