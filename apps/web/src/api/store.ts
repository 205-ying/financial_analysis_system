/**
 * 门店相关接口
 */
import request from '@/utils/request'
import type { ApiResponse, StoreInfo, PageData, PageParams } from '@/types'

/**
 * 获取门店列表
 */
export function getStoreList(params?: PageParams): Promise<ApiResponse<PageData<StoreInfo>>> {
  return request.get('/stores', { params })
}

/**
 * 获取所有门店（不分页）
 */
export function getAllStores(): Promise<ApiResponse<StoreInfo[]>> {
  return request.get('/stores/all')
}

/**
 * 获取门店详情
 */
export function getStoreDetail(id: number): Promise<ApiResponse<StoreInfo>> {
  return request.get(`/stores/${id}`)
}
