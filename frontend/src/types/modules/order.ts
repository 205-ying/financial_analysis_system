/**
 * 订单相关类型定义
 */
import type { PageParams } from './common'

export interface OrderInfo {
  id: number
  store_id: number
  store_name: string
  order_no: string
  amount: number
  channel: string
  order_time: string
  remark?: string
  created_at: string
}

export interface OrderQuery extends PageParams {
  store_id?: number
  channel?: string
  start_date?: string
  end_date?: string
  order_no?: string
}
