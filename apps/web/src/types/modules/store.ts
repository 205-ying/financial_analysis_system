/**
 * 门店相关类型定义
 */

export interface StoreInfo {
  id: number
  name: string
  code: string
  address?: string
  manager?: string
  phone?: string
  is_active: boolean
  created_at: string
}
