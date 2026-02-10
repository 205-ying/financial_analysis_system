/**
 * 菜品销售分析相关接口
 */
import request from '@/utils/request'
import type {
  ApiResponse,
  ProductAnalysisQuery,
  ProductSalesRankingItem,
  CategorySalesItem,
  ProductProfitItem,
  ProductABCItem,
  ProductStoreCrossItem
} from '@/types'

/**
 * 获取菜品销量排行榜
 */
export function getProductSalesRanking(
  params: ProductAnalysisQuery
): Promise<ApiResponse<ProductSalesRankingItem[]>> {
  return request.get('/product-analysis/sales-ranking', { params })
}

/**
 * 获取品类销售占比分布
 */
export function getCategoryDistribution(
  params: ProductAnalysisQuery
): Promise<ApiResponse<CategorySalesItem[]>> {
  return request.get('/product-analysis/category-distribution', { params })
}

/**
 * 获取菜品毛利贡献排行
 */
export function getProductProfitContribution(
  params: ProductAnalysisQuery
): Promise<ApiResponse<ProductProfitItem[]>> {
  return request.get('/product-analysis/profit-contribution', { params })
}

/**
 * 获取菜品ABC分类
 */
export function getProductABCClassification(
  params: ProductAnalysisQuery
): Promise<ApiResponse<ProductABCItem[]>> {
  return request.get('/product-analysis/abc-classification', { params })
}

/**
 * 获取菜品-门店交叉分析
 */
export function getProductStoreCross(
  params: ProductAnalysisQuery
): Promise<ApiResponse<ProductStoreCrossItem[]>> {
  return request.get('/product-analysis/product-store-cross', { params })
}
