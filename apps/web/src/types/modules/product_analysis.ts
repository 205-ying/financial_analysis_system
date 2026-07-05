/**
 * 菜品销售分析相关类型定义
 */

/** 菜品分析查询参数 */
export interface ProductAnalysisQuery {
  start_date?: string
  end_date?: string
  store_id?: number
  top_n?: number
  sort_by?: 'quantity' | 'revenue'
}

/** 菜品销量排行项 */
export interface ProductSalesRankingItem {
  rank: number
  product_name: string
  product_category: string | null
  total_quantity: number
  total_revenue: number
  net_revenue: number
  order_count: number
  gross_profit: number | null
}

/** 品类销售分布项 */
export interface CategorySalesItem {
  category_name: string
  revenue: number
  quantity: number
  percentage: number
}

/** 菜品毛利贡献项 */
export interface ProductProfitItem {
  rank: number
  product_name: string
  product_category: string | null
  total_revenue: number
  total_cost: number
  gross_profit: number
  profit_margin: number
}

/** 菜品ABC分类项 */
export interface ProductABCItem {
  product_name: string
  total_revenue: number
  percentage: number
  cumulative_percentage: number
  abc_class: 'A' | 'B' | 'C'
}

/** 菜品-门店交叉分析项 */
export interface ProductStoreCrossItem {
  store_name: string
  product_name: string
  quantity: number
  revenue: number
}
