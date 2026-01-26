/**
 * 订单相关接口
 */
import request from '@/utils/request'
import type { ApiResponse, OrderInfo, OrderQuery, OrderCreate, PageData } from '@/types'

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

/**
 * 创建订单
 */
export function createOrder(data: OrderCreate): Promise<ApiResponse<OrderInfo>> {
  return request.post('/orders', data)
}

/**
 * 导出订单
 */
export function exportOrders(params: OrderQuery): Promise<Blob> {
  return request.get('/orders/export', { 
    params,
    responseType: 'blob'
  })
}
