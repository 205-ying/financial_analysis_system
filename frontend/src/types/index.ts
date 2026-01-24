/**
 * 类型定义统一导出
 * 按模块组织，便于维护和扩展
 */

// 通用类型
export * from './modules/common'

// 认证相关
export * from './modules/auth'

// 门店相关
export * from './modules/store'

// 费用相关
export * from './modules/expense'

// 订单相关
export * from './modules/order'

// KPI 相关
export * from './modules/kpi'

// 保留旧的 api.ts 的导出以保持向后兼容
// 未来可以逐步迁移到按模块导入
