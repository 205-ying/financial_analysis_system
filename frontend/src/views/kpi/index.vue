<template>
  <div class="kpi-container">
    <!-- 筛选条件 -->
    <filter-bar ref="filterBarRef" @query="handleQuery" />

    <el-row :gutter="20">
      <!-- 成本结构分析 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><PieChart /></el-icon>
                成本结构分析
              </span>
            </div>
          </template>
          <div ref="categoryChartRef" class="chart-container"></div>
          <div class="chart-legend">
            <div
              v-for="item in expenseCategoryData"
              :key="item.category_name"
              class="legend-item"
            >
              <span class="legend-label">{{ item.category_name }}:</span>
              <span class="legend-value">￥{{ formatNumber(item.amount || 0) }}</span>
              <span class="legend-percent">({{ (item.percentage || 0).toFixed(2) }}%)</span>
            </div>
          </div>
        </el-card>
      </el-col>

      <!-- 门店对比 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><Histogram /></el-icon>
                门店利润排名
              </span>
              <el-select v-model="topN" size="small" class="kpi-select" @change="handleTopNChange">
                <el-option label="Top 5" :value="5" />
                <el-option label="Top 10" :value="10" />
                <el-option label="Top 15" :value="15" />
                <el-option label="全部" :value="999" />
              </el-select>
            </div>
          </template>
          <div ref="rankingChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 门店详细数据表格 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><List /></el-icon>
            门店详细数据
          </span>
        </div>
      </template>

      <el-table :data="storeRankingData" stripe border>
        <el-table-column type="index" label="排名" width="80" align="center" />
        <el-table-column prop="store_name" label="门店名称" min-width="150" />
        <el-table-column label="营收" width="150" align="right">
          <template #default="{ row }">
            <span class="revenue-cell">¥{{ formatNumber(row.revenue || row.total_revenue || 0) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="成本" width="150" align="right">
          <template #default="{ row }">
            <span class="cost-cell">¥{{ formatNumber(row.cost || row.total_cost || 0) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="利润" width="150" align="right">
          <template #default="{ row }">
            <span class="profit-cell">¥{{ formatNumber(row.profit || row.total_profit || 0) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="利润率" width="120" align="right">
          <template #default="{ row }">
            <el-tag :type="getProfitRateType((row.profit_margin !== undefined ? row.profit_margin / 100 : (row.profit_rate || 0)))">
              {{ (row.profit_margin !== undefined ? row.profit_margin : ((row.profit_rate || 0) * 100)).toFixed(2) }}%
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { PieChart, Histogram, List } from '@element-plus/icons-vue'
import { FilterBar } from '@/components'
import { useECharts, type ECOption } from '@/composables/useECharts'
import { getExpenseCategory, getStoreRanking } from '@/api/kpi'
import type { ExpenseCategoryItem, StoreRankingItem, KPIQuery } from '@/types'
import { COLORS, CHART_PALETTE } from '@/utils/colors'

// 筛选栏引用
const filterBarRef = ref()

// 费用分类数据
const expenseCategoryData = ref<ExpenseCategoryItem[]>([])

// 门店排名数据
const storeRankingData = ref<StoreRankingItem[]>([])

// Top N
const topN = ref(10)

// 当前查询参数
const currentQuery = ref<KPIQuery>({})

// 费用分类图表
const categoryChartRef = ref<HTMLElement | null>(null)
const {
  setOption: setCategoryOption,
  showLoading: showCategoryLoading,
  hideLoading: hideCategoryLoading
} = useECharts(categoryChartRef)

// 门店排名图表
const rankingChartRef = ref<HTMLElement | null>(null)
const {
  setOption: setRankingOption,
  showLoading: showRankingLoading,
  hideLoading: hideRankingLoading
} = useECharts(rankingChartRef)

/**
 * 格式化数字
 */
const formatNumber = (value: number): string => {
  if (value === 0) return '0'
  if (!value) return '0'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/**
 * 获取利润率标签类型
 */
const getProfitRateType = (rate: number) => {
  if (rate >= 0.3) return 'success'
  if (rate >= 0.15) return ''
  if (rate >= 0.05) return 'warning'
  return 'danger'
}

/**
 * 处理查询
 */
const handleQuery = async (filters: KPIQuery) => {
  currentQuery.value = { ...filters, top_n: topN.value }
  await Promise.all([loadExpenseCategory(), loadStoreRanking()])
}

/**
 * 处理 TopN 改变
 */
const handleTopNChange = () => {
  currentQuery.value.top_n = topN.value
  loadStoreRanking()
}

const isRecord = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null

const getArrayField = <T>(value: unknown, key: string): T[] | null => {
  if (!isRecord(value)) return null
  const field = value[key]
  return Array.isArray(field) ? (field as T[]) : null
}

const toNumber = (value: unknown): number => {
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0
  if (typeof value === 'string') {
    const num = Number(value)
    return Number.isFinite(num) ? num : 0
  }
  return 0
}

/**
 * 加载费用分类数据
 */
const loadExpenseCategory = async () => {
  try {
    showCategoryLoading()
    const { data } = await getExpenseCategory(currentQuery.value)
    // 后端可能返回 {categories: [...]} 或直接返回数组
    const raw: unknown = data
    const extracted = getArrayField<ExpenseCategoryItem>(raw, 'categories')
    const categories = extracted ?? (Array.isArray(raw) ? (raw as ExpenseCategoryItem[]) : [])
    expenseCategoryData.value = categories
    renderCategoryChart(categories)
  } catch (error) {
    void error
  } finally {
    hideCategoryLoading()
  }
}

/**
 * 渲染费用分类图表（环形图）
 */
const renderCategoryChart = (data: ExpenseCategoryItem[]) => {
  const chartData = data.map(item => ({
    name: item.category_name,
    value: item.amount
  }))

  const option: ECOption = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: ¥{c} ({d}%)'
    },
    legend: {
      top: 'bottom',
      left: 'center'
    },
    series: [
      {
        name: '费用占比',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: COLORS.WHITE,
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: chartData
      }
    ],
    color: CHART_PALETTE.CATEGORY
  }

  setCategoryOption(option, true)
}

/**
 * 加载门店排名数据
 */
const loadStoreRanking = async () => {
  try {
    showRankingLoading()
    const { data } = await getStoreRanking(currentQuery.value)
    // 后端可能返回 {stores: [...]} 或直接返回数组
    const raw: unknown = data
    const extracted = getArrayField<StoreRankingItem>(raw, 'stores')
    const stores = extracted ?? (Array.isArray(raw) ? (raw as StoreRankingItem[]) : [])
    storeRankingData.value = stores
    renderRankingChart(stores as unknown as Array<Record<string, unknown>>)
  } catch (error) {
    void error
  } finally {
    hideRankingLoading()
  }
}

/**
 * 渲染门店排名图表（柱状图）
 */
const renderRankingChart = (data: Array<Record<string, unknown>>) => {
  const storeNames = data.map((item) => String(item['store_name'] ?? ''))
  // 兼容不同字段名：profit/total_profit
  const profits = data.map((item) => toNumber(item['profit'] ?? item['total_profit'] ?? 0))
  // 兼容不同字段名：profit_margin(可能已是百分比) / profit_rate(小数)
  const profitRates = data.map((item) => {
    if (item['profit_margin'] !== undefined && item['profit_margin'] !== null) {
      return toNumber(item['profit_margin'])
    }
    return toNumber(item['profit_rate']) * 100
  })

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: unknown) => {
        const list = Array.isArray(params) ? params : []
        const axisValue = (list[0] as { axisValue?: unknown } | undefined)?.axisValue
        const title = typeof axisValue === 'string' ? axisValue : ''
        let result = `<div style="font-weight: bold; margin-bottom: var(--spacing-1);">${title}</div>`
        list.forEach((raw) => {
          const item = raw as { seriesName?: unknown; marker?: unknown; value?: unknown }
          const seriesName = typeof item.seriesName === 'string' ? item.seriesName : ''
          const marker = typeof item.marker === 'string' ? item.marker : ''
          const valueNum = typeof item.value === 'number' ? item.value : Number(item.value)
          const safeValue = Number.isFinite(valueNum) ? valueNum : 0
          if (seriesName === '利润') {
            result += `<div>${marker}${seriesName}: ¥${safeValue.toLocaleString('zh-CN', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}</div>`
          } else {
            result += `<div>${marker}${seriesName}: ${safeValue.toFixed(2)}%</div>`
          }
        })
        return result
      }
    },
    legend: {
      data: ['利润', '利润率'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 60,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: storeNames,
      axisLabel: {
        rotate: storeNames.length > 5 ? 45 : 0,
        interval: 0
      }
    },
    yAxis: [
      {
        type: 'value',
        name: '利润(元)',
        position: 'left',
        axisLabel: {
          formatter: (value: number) => {
            if (value >= 10000) {
              return (value / 10000).toFixed(1) + 'w'
            }
            return value.toString()
          }
        }
      },
      {
        type: 'value',
        name: '利润率(%)',
        position: 'right',
        axisLabel: {
          formatter: '{value}%'
        }
      }
    ],
    series: [
      {
        name: '利润',
        type: 'bar',
        data: profits,
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: COLORS.PRIMARY },
              { offset: 1, color: COLORS.PRIMARY_LIGHT }
            ]
          }
        },
        barWidth: '40%'
      },
      {
        name: '利润率',
        type: 'line',
        yAxisIndex: 1,
        data: profitRates,
        itemStyle: { color: COLORS.SUCCESS },
        lineStyle: { width: 3 },
        symbol: 'circle',
        symbolSize: 8
      }
    ]
  }

  setRankingOption(option, true)
}

onMounted(() => {
  // 初始化时会由 FilterBar 自动触发查询
})
</script>

<style scoped lang="scss">
.kpi-container {
  padding: var(--spacing-5) var(--spacing-5) var(--spacing-6);
  background-color: var(--color-bg-secondary);
  min-height: calc(100vh - var(--spacing-8)); // 减去顶部导航高度
}

.chart-card,
.table-card {
  margin-bottom: var(--spacing-5);

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-4) 0;

    .title {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);
      font-size: var(--font-size-lg);
      font-weight: var(--font-weight-semibold);
      color: var(--color-text-primary);

      .el-icon {
        color: var(--color-primary);
        font-size: var(--font-size-xl);
      }
    }
  }

  .chart-container {
    width: 100%;
    height: calc(var(--spacing-6) * 12.5); // 400px
    border-radius: var(--border-radius-sm);
    overflow: hidden;
  }

  .chart-legend {
    margin-top: var(--spacing-5);
    padding: var(--spacing-4);
    background: var(--color-bg-secondary);
    border-radius: var(--border-radius-sm);
    border: var(--border-width-thin) solid var(--color-border-light);

    .legend-item {
      display: flex;
      justify-content: space-between;
      padding: var(--spacing-2) 0;
      border-bottom: var(--border-width-thin) solid var(--color-border-light);
      transition: background-color var(--transition-duration-fast) var(--transition-timing-function-base);

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background-color: var(--color-bg-tertiary);
        padding-left: var(--spacing-2);
        padding-right: var(--spacing-2);
        margin: 0 calc(-1 * var(--spacing-2));
        border-radius: var(--border-radius-sm);
      }

      .legend-label {
        color: var(--color-text-secondary);
        font-weight: var(--font-weight-medium);
        font-size: var(--font-size-sm);
      }

      .legend-value {
        color: var(--color-primary);
        font-weight: var(--font-weight-semibold);
        font-size: var(--font-size-sm);
      }

      .legend-percent {
        color: var(--color-text-tertiary);
        font-size: var(--font-size-sm);
      }
    }
  }

  // ===== 卡片统一样式 =====
  :deep(.chart-card),
  :deep(.table-card) {
    border-radius: var(--border-radius-md);
    border: var(--border-width-thin) solid var(--color-border-light);
    background-color: var(--color-bg-primary);
    box-shadow: var(--shadow-sm);
    transition: box-shadow var(--transition-duration-base) var(--transition-timing-function-base);
    overflow: hidden;

    &:hover {
      box-shadow: var(--shadow-md);
    }

    .el-card__header {
      background-color: var(--color-bg-secondary);
      border-bottom: var(--border-width-thin) solid var(--color-border-light);
      padding: var(--spacing-4) var(--spacing-5);

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0;
      }
    }

    .el-card__body {
      padding: var(--spacing-5);
    }
  }

  // ===== 数据表格统一样式 =====
  :deep(.el-table) {
    border-radius: var(--border-radius-sm);
    overflow: hidden;
    border: var(--border-width-thin) solid var(--color-border-light);

    &.el-table--border {
      border: var(--border-width-thin) solid var(--color-border-light);
    }

    &.el-table--striped {
      .el-table__body {
        tr.el-table__row--striped {
          td {
            background-color: var(--color-bg-secondary);
          }

          &:hover {
            td {
              background-color: var(--color-gray-50);
            }
          }
        }
      }
    }

    // 表头样式
    .el-table__header-wrapper {
      th {
        background-color: var(--color-bg-secondary) !important;
        color: var(--color-text-secondary) !important;
        font-weight: var(--font-weight-semibold);
        font-size: var(--font-size-sm);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: var(--border-width-thin) solid var(--color-border-base);
        padding: var(--spacing-3) var(--spacing-3);

        .cell {
          line-height: 1.4;
        }
      }
    }

    // 表格主体
    .el-table__body-wrapper {
      .el-table__row {
        transition: background-color var(--transition-duration-fast) var(--transition-timing-function-base);

        &:hover {
          td {
            background-color: var(--color-bg-tertiary);
          }
        }

        td {
          padding: var(--spacing-3) var(--spacing-3);
          border-bottom: var(--border-width-thin) solid var(--color-border-light);
          color: var(--color-text-secondary);
          font-size: var(--font-size-sm);
          line-height: 1.5;

          &:first-child {
            color: var(--color-text-tertiary);
            font-weight: var(--font-weight-medium);
          }
        }
      }
    }

    // KPI 表格单元格样式
    .el-table__row {
      .revenue-cell {
        font-weight: var(--font-weight-semibold);
        color: var(--color-success);
      }

      .cost-cell {
        font-weight: var(--font-weight-semibold);
        color: var(--color-warning);
      }

      .profit-cell {
        font-weight: var(--font-weight-semibold);
        color: var(--color-primary);
      }
    }

    // 标签样式
    .el-tag {
      border-radius: var(--border-radius-sm);
      font-weight: var(--font-weight-medium);
      font-size: var(--font-size-xs);
      padding: var(--spacing-1) var(--spacing-2);
      transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

      &:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
      }
    }
  }

  // ===== KPI 选择器样式 =====
  .kpi-select {
    width: calc(var(--spacing-6) * 3.75); // 120px

    :deep(.el-input__wrapper) {
      border-radius: var(--border-radius-sm);
      border: var(--border-width-thin) solid var(--color-border-light);
      background-color: var(--color-bg-primary);
      transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

      &:hover {
        border-color: var(--color-border-base);
      }

      &.is-focus {
        border-color: var(--color-primary);
        box-shadow: 0 0 0 1px var(--color-primary-lightest);
      }
    }

    :deep(.el-select__caret) {
      color: var(--color-text-tertiary);
    }
  }

  // ===== 网格布局 =====
  :deep(.el-row) {
    margin-bottom: var(--spacing-5);

    &:last-child {
      margin-bottom: 0;
    }
  }

  // ===== 加载状态 =====
  :deep(.el-loading-mask) {
    background-color: rgba(var(--color-bg-primary-rgb), 0.8);
    backdrop-filter: blur(4px);

    .el-loading-spinner {
      .circular {
        .path {
          stroke: var(--color-primary);
        }
      }

      .el-loading-text {
        color: var(--color-text-secondary);
        margin-top: var(--spacing-2);
        font-size: var(--font-size-sm);
      }
    }
  }

  // ===== 响应式调整 =====
  @media (max-width: var(--breakpoint-md)) {
    padding: var(--spacing-4);

    :deep(.el-col) {
      margin-bottom: var(--spacing-4);

      &:last-child {
        margin-bottom: 0;
      }
    }

    :deep(.chart-card),
    :deep(.table-card) {
      .el-card__header {
        padding: var(--spacing-3) var(--spacing-4);
      }

      .el-card__body {
        padding: var(--spacing-4);
      }
    }

    :deep(.el-table) {
      .el-table__header-wrapper,
      .el-table__body-wrapper {
        overflow-x: auto;

        th,
        td {
          white-space: nowrap;
        }
      }
    }

    .chart-container {
      height: calc(var(--spacing-6) * 9.375); // 300px
    }
  }

  @media (max-width: var(--breakpoint-sm)) {
    padding: var(--spacing-3);

    :deep(.chart-card),
    :deep(.table-card) {
      .el-card__header {
        padding: var(--spacing-3);
      }

      .el-card__body {
        padding: var(--spacing-3);
      }
    }

    .chart-container {
      height: calc(var(--spacing-6) * 7.8125); // 250px
    }
  }
}
</style>
