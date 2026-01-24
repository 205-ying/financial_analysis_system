/**
 * 订单相关接口
 */
import request from '@/utils/request'
import type { ApiResponse, OrderInfo, OrderQuery, PageData } from '@/types'

/**
 * 获取订单列表
 */
export function getOrderList(params: OrderQuery): Promise<ApiResponse<PageData<OrderInfo>>> {
  return request.get('/orders', { params })
}

/**
 * 获取订单详情
 */
export function getOrderDetail(id: number): Promise<ApiResponse<OrderInfo>> {
  return request.get(`/orders/${id}`)
}
