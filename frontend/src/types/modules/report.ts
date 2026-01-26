/**
 * 报表模块类型定义
 */

// 报表查询参数
export interface ReportQuery {
  start_date: string   // YYYY-MM-DD
  end_date: string     // YYYY-MM-DD
  store_id?: number    // 可选门店筛选
  top_n?: number       // TOP N 限制
}

// 日汇总报表行
export interface DailySummaryRow {
  biz_date: string             // 业务日期
  store_id: number             // 门店ID
  store_name: string           // 门店名称
  revenue: number              // 营收
  net_revenue: number          // 净营收
  cost_total: number           // 总成本
  expense_total: number        // 费用总额
  order_count: number          // 订单数
  gross_profit: number         // 毛利
  operating_profit: number     // 营业利润
  gross_profit_rate?: number | null    // 毛利率（%）
  operating_profit_rate?: number | null // 营业利润率（%）
  cost_material: number        // 原材料成本
  cost_labor: number           // 人工成本
  discount_amount: number      // 优惠金额
  refund_amount: number        // 退款金额
}

// 月汇总报表行
export interface MonthlySummaryRow {
  year: number                 // 年份
  month: number                // 月份
  store_id: number             // 门店ID
  store_name: string           // 门店名称
  revenue: number              // 营收
  net_revenue: number          // 净营收
  cost_total: number           // 总成本
  expense_total: number        // 费用总额
  order_count: number          // 订单数
  gross_profit: number         // 毛利
  operating_profit: number     // 营业利润
  gross_profit_rate?: number | null    // 毛利率（%）
  operating_profit_rate?: number | null // 营业利润率（%）
  avg_daily_revenue: number    // 日均营收
  avg_daily_order_count: number // 日均订单数
  day_count: number            // 天数
}

// 门店绩效行
export interface StorePerformanceRow {
  store_id: number             // 门店ID
  store_name: string           // 门店名称
  revenue: number              // 营收
  net_revenue: number          // 净营收
  order_count: number          // 订单数
  avg_order_amount: number     // 平均订单金额
  gross_profit: number         // 毛利
  operating_profit: number     // 营业利润
  gross_profit_rate?: number | null    // 毛利率（%）
  operating_profit_rate?: number | null // 营业利润率（%）
  revenue_rank: number         // 营收排名
  profit_rank: number          // 利润排名
}

// 费用明细行
export interface ExpenseBreakdownRow {
  expense_type_id: number      // 费用科目ID
  type_code: string            // 科目代码
  type_name: string            // 科目名称
  category: string             // 费用类别
  total_amount: number         // 总金额
  record_count: number         // 记录数
  avg_amount: number           // 平均金额
  percentage: number           // 占比（%）
}

// 报表响应数据
export interface ReportResponse<T> {
  code: number
  message: string
  data: T[]
}
