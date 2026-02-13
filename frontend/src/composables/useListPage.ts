import { ref } from 'vue'

type ListResponse<T> = {
  data: {
    items: T[]
    total: number
  }
}

type FetchListFn<T, Q> = (query: Q) => Promise<ListResponse<T>>

export function useListPage<T, Q extends { page: number; page_size: number }>(
  queryForm: Q,
  fetchList: FetchListFn<T, Q>
) {
  const tableData = ref<T[]>([])
  const loading = ref(false)
  const total = ref(0)

  const loadTableData = async () => {
    try {
      loading.value = true
      const { data } = await fetchList(queryForm)
      tableData.value = data.items
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  const applyDateRange = (dateRange?: [string, string]) => {
    ;(queryForm as Q & { start_date?: string; end_date?: string }).start_date = dateRange
      ? dateRange[0]
      : undefined
    ;(queryForm as Q & { start_date?: string; end_date?: string }).end_date = dateRange
      ? dateRange[1]
      : undefined
  }

  const handleQuery = async (dateRange?: [string, string]) => {
    applyDateRange(dateRange)
    queryForm.page = 1
    await loadTableData()
  }

  const handleReset = async (
    resetQueryFields: () => void,
    clearDateRange: () => void
  ) => {
    resetQueryFields()
    queryForm.page = 1
    queryForm.page_size = 20
    clearDateRange()
    await loadTableData()
  }

  return {
    tableData,
    loading,
    total,
    loadTableData,
    handleQuery,
    handleReset,
  }
}

export default useListPage