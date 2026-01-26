/**
 * 门店状态管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getStoreList } from '@/api/store'
import { useAuthStore } from './auth'

export interface Store {
  id: number
  code: string
  name: string
  address?: string
  phone?: string
  is_active: boolean
}

export const useStoreStore = defineStore('store', () => {
  const authStore = useAuthStore()
  
  // State
  const allStores = ref<Store[]>([])
  const loading = ref(false)

  // Getters
  /**
   * 用户可访问的门店列表（根据数据权限过滤）
   */
  const accessibleStoreList = computed(() => {
    const accessibleIds = authStore.accessibleStores
    
    // null 表示可以访问所有门店
    if (accessibleIds === null) {
      return allStores.value
    }
    
    // 过滤出用户有权限的门店
    return allStores.value.filter(store => accessibleIds.includes(store.id))
  })

  /**
   * 用户可访问的门店选项（用于下拉框）
   * 添加"全部"选项时表示"权限范围内全部门店"
   */
  const accessibleStoreOptions = computed(() => {
    return accessibleStoreList.value.map(store => ({
      label: store.name,
      value: store.id
    }))
  })

  // Actions
  /**
   * 获取所有门店列表（不分页）
   * 注意：最多获取500个门店（后端限制）
   */
  async function fetchAllStores() {
    if (loading.value) return
    
    loading.value = true
    try {
      const response = await getStoreList({ page: 1, page_size: 500 })
      allStores.value = response.data.items || []
      
      // 如果返回500条，可能还有更多数据
      if (allStores.value.length === 500) {
        console.warn('门店数量达到500上限，可能存在未加载的门店')
      }
    } catch (error) {
      console.error('获取门店列表失败：', error)
      allStores.value = []
      throw error
    } finally {
      loading.value = false
    }
  }

  /**
   * 检查是否可以访问指定门店
   */
  function canAccessStore(storeId: number): boolean {
    const accessibleIds = authStore.accessibleStores
    
    // null 表示可以访问所有门店
    if (accessibleIds === null) {
      return true
    }
    
    return accessibleIds.includes(storeId)
  }

  /**
   * 根据ID获取门店名称
   */
  function getStoreName(storeId: number): string {
    const store = allStores.value.find(s => s.id === storeId)
    return store?.name || `门店${storeId}`
  }

  return {
    // State
    allStores,
    loading,
    // Getters
    accessibleStoreList,
    accessibleStoreOptions,
    // Actions
    fetchAllStores,
    canAccessStore,
    getStoreName
  }
})
