import { computed, ref, toRaw, type Ref } from 'vue'
import { ElMessage } from 'element-plus'

type DateRange = [string, string] | null | undefined

type TableQuery = {
  page?: number
  page_size?: number
  start_date?: string
  end_date?: string
}

type PagePayload<T> = {
  items?: T[]
  total?: number
  page?: number
  page_size?: number
  total_pages?: number
}

type ListResponse<T> = {
  data?: PagePayload<T>
}

type FetchListFn<T, Q> = (query: Q) => Promise<ListResponse<T>>

export interface InteractiveTableOptions<Q extends TableQuery> {
  defaultQuery?: Partial<Q>
  dateRange?: Ref<unknown>
  pageSize?: number
  errorMessage?: string
  emptyOnError?: boolean
}

const formatUpdatedAt = (date: Date | null) => {
  if (!date) return ''
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(date)
}

const assignQuery = <Q extends TableQuery>(queryForm: Q, nextQuery: Partial<Q>) => {
  const target = queryForm as unknown as Record<string, unknown>
  const source = nextQuery as Record<string, unknown>
  const keys = new Set([...Object.keys(target), ...Object.keys(source)])

  keys.forEach(key => {
    target[key] = source[key]
  })
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')

  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

export function useInteractiveTable<T, Q extends TableQuery>(
  queryForm: Q,
  fetchList: FetchListFn<T, Q>,
  options: InteractiveTableOptions<Q> = {}
) {
  const defaultPageSize = options.pageSize ?? queryForm.page_size ?? 20
  const initialQuery = { ...(toRaw(queryForm) as Q) } as Partial<Q>
  const activeDateRange = (options.dateRange ?? ref<DateRange>(undefined)) as Ref<DateRange>

  const tableData = ref<T[]>([])
  const loading = ref(false)
  const total = ref(0)
  const totalPages = ref(0)
  const lastUpdatedAt = ref<Date | null>(null)
  const lastUpdatedLabel = computed(() => formatUpdatedAt(lastUpdatedAt.value))

  const getDefaultQuery = () => ({
    ...initialQuery,
    ...options.defaultQuery,
    page: 1,
    page_size: defaultPageSize,
  }) as Partial<Q>

  const applyDateRange = (range: DateRange = activeDateRange.value) => {
    const target = queryForm as unknown as TableQuery
    target.start_date = range ? range[0] : undefined
    target.end_date = range ? range[1] : undefined
  }

  const loadTableData = async () => {
    loading.value = true
    applyDateRange()

    try {
      const response = await fetchList(queryForm)
      const payload = response.data ?? {}
      const items = payload.items ?? []

      tableData.value = items
      total.value = payload.total ?? items.length
      totalPages.value = payload.total_pages ?? 0

      if (payload.page) queryForm.page = payload.page
      if (payload.page_size) queryForm.page_size = payload.page_size

      lastUpdatedAt.value = new Date()
    } catch (error) {
      if (options.emptyOnError !== false) {
        tableData.value = []
        total.value = 0
        totalPages.value = 0
      }

      ElMessage.error(options.errorMessage ?? (error instanceof Error ? error.message : '数据加载失败'))
    } finally {
      loading.value = false
    }
  }

  const handleQuery = async (range?: DateRange) => {
    activeDateRange.value = range
    queryForm.page = 1
    await loadTableData()
  }

  const handlePageChange = async () => {
    await loadTableData()
  }

  const handlePageSizeChange = async () => {
    queryForm.page = 1
    await loadTableData()
  }

  const handleReset = async (
    resetFields?: () => void,
    clearDateRange?: () => void
  ) => {
    assignQuery(queryForm, getDefaultQuery())
    resetFields?.()
    activeDateRange.value = undefined
    clearDateRange?.()
    applyDateRange(undefined)
    await loadTableData()
  }

  const refresh = async () => {
    await loadTableData()
  }

  return {
    tableData,
    loading,
    total,
    totalPages,
    lastUpdatedAt,
    lastUpdatedLabel,
    loadTableData,
    handleQuery,
    handlePageChange,
    handlePageSizeChange,
    handleReset,
    refresh,
  }
}

export default useInteractiveTable
