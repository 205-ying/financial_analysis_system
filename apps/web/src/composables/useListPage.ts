import { useInteractiveTable } from './useInteractiveTable'

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
  const table = useInteractiveTable<T, Q>(queryForm, fetchList)

  const handleQuery = async (dateRange?: [string, string]) => {
    await table.handleQuery(dateRange)
  }

  const handleReset = async (
    resetQueryFields: () => void,
    clearDateRange: () => void
  ) => {
    await table.handleReset(resetQueryFields, clearDateRange)
  }

  return {
    tableData: table.tableData,
    loading: table.loading,
    total: table.total,
    loadTableData: table.loadTableData,
    handleQuery,
    handleReset,
  }
}

export default useListPage
