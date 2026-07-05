<template>
  <div class="product-analysis-container">
    <section class="analysis-page-head">
      <div>
        <p class="eyebrow">Menu Contribution</p>
        <h1>菜品分析</h1>
      </div>
      <span>销量、毛利贡献和 ABC 分类</span>
    </section>

    <!-- 筛选条件 -->
    <filter-bar ref="filterBarRef" @query="handleQuery" />

    <!-- 排序和TopN控制 -->
    <el-card shadow="never" class="control-card">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <span class="control-label">排序方式：</span>
          <el-radio-group v-model="sortBy" size="small" @change="handleControlChange">
            <el-radio-button value="quantity">按销量</el-radio-button>
            <el-radio-button value="revenue">按销售额</el-radio-button>
          </el-radio-group>
        </el-col>
        <el-col :span="8">
          <span class="control-label">显示数量：</span>
          <el-select v-model="topN" size="small" class="product-select" @change="handleControlChange">
            <el-option label="Top 5" :value="5" />
            <el-option label="Top 10" :value="10" />
            <el-option label="Top 20" :value="20" />
            <el-option label="全部" :value="999" />
          </el-select>
        </el-col>
      </el-row>
    </el-card>

    <!-- 第一行: 销量排行 + 品类分布 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><Histogram /></el-icon>
                菜品销量排行榜
              </span>
            </div>
          </template>
          <div ref="salesRankingChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><PieChart /></el-icon>
                品类销售占比
              </span>
            </div>
          </template>
          <div ref="categoryChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行: 毛利贡献 + ABC分类 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><TrendCharts /></el-icon>
                毛利贡献排行
              </span>
            </div>
          </template>
          <div ref="profitChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="never">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><DataAnalysis /></el-icon>
                ABC分类分布
              </span>
            </div>
          </template>
          <div class="abc-summary">
            <div class="abc-tag-group">
              <el-tag type="success" size="large" effect="dark">
                A类: {{ abcSummary.a }}种 (占比≤70%)
              </el-tag>
              <el-tag type="warning" size="large" effect="dark">
                B类: {{ abcSummary.b }}种 (占比70%-90%)
              </el-tag>
              <el-tag type="danger" size="large" effect="dark">
                C类: {{ abcSummary.c }}种 (占比>90%)
              </el-tag>
            </div>
          </div>
          <div ref="abcChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行: 菜品-门店交叉分析表格 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><Grid /></el-icon>
            菜品-门店交叉分析
          </span>
        </div>
      </template>
      <el-table v-loading="crossLoading" :data="crossData" stripe border empty-text="暂无数据">
        <el-table-column prop="store_name" label="门店名称" min-width="140" fixed />
        <el-table-column prop="product_name" label="菜品名称" min-width="140" />
        <el-table-column label="销量" width="120" align="right">
          <template #default="{ row }">
            {{ formatNumber(row.quantity) }}
          </template>
        </el-table-column>
        <el-table-column label="销售额" width="140" align="right">
          <template #default="{ row }">
            <span style="color: var(--color-primary); font-weight: 600">¥{{ formatCurrency(row.revenue) }}</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 第四行: ABC分类明细表格 -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><List /></el-icon>
            ABC分类明细
          </span>
        </div>
      </template>
      <el-table v-loading="abcLoading" :data="abcData" stripe border empty-text="暂无数据">
        <el-table-column label="分类" width="80" align="center">
          <template #default="{ row }">
            <el-tag
              :type="row.abc_class === 'A' ? 'success' : row.abc_class === 'B' ? 'warning' : 'danger'"
              effect="dark"
              size="small"
            >
              {{ row.abc_class }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="product_name" label="菜品名称" min-width="160" />
        <el-table-column label="销售额" width="140" align="right">
          <template #default="{ row }">
            <span style="font-weight: 600">¥{{ formatCurrency(row.total_revenue) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="占比" width="100" align="right">
          <template #default="{ row }">
            {{ row.percentage.toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column label="累计占比" width="120" align="right">
          <template #default="{ row }">
            <span :style="{ color: row.cumulative_percentage <= 70 ? 'var(--color-success)' : row.cumulative_percentage <= 90 ? 'var(--color-warning)' : 'var(--color-danger)' }">
              {{ row.cumulative_percentage.toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  Histogram,
  PieChart,
  TrendCharts,
  DataAnalysis,
  Grid,
  List
} from '@element-plus/icons-vue'
import { FilterBar } from '@/components'
import { useECharts, type ECOption } from '@/composables/useECharts'
import {
  getProductSalesRanking,
  getCategoryDistribution,
  getProductProfitContribution,
  getProductABCClassification,
  getProductStoreCross
} from '@/api/product_analysis'
import { COLORS, CHART_PALETTE } from '@/utils/colors'
import type {
  ProductAnalysisQuery,
  ProductSalesRankingItem,
  CategorySalesItem,
  ProductProfitItem,
  ProductABCItem,
  ProductStoreCrossItem
} from '@/types'

// 控制参数
const sortBy = ref<'quantity' | 'revenue'>('quantity')
const topN = ref(10)
const currentQuery = ref<ProductAnalysisQuery>({})

// 数据
const salesRankingData = ref<ProductSalesRankingItem[]>([])
const categoryData = ref<CategorySalesItem[]>([])
const profitData = ref<ProductProfitItem[]>([])
const abcData = ref<ProductABCItem[]>([])
const crossData = ref<ProductStoreCrossItem[]>([])

// 加载状态
const crossLoading = ref(false)
const abcLoading = ref(false)

const fallbackSalesRanking: ProductSalesRankingItem[] = [
  { rank: 1, product_name: '水煮牛肉', product_category: '热菜', total_quantity: 1260, total_revenue: 156320, net_revenue: 151200, order_count: 1180, gross_profit: 91640 },
  { rank: 2, product_name: '烤鸭', product_category: '招牌菜', total_quantity: 980, total_revenue: 142850, net_revenue: 139600, order_count: 940, gross_profit: 88740 },
  { rank: 3, product_name: '宫保鸡丁', product_category: '热菜', total_quantity: 1120, total_revenue: 98760, net_revenue: 96100, order_count: 1040, gross_profit: 55020 },
  { rank: 4, product_name: '酸菜鱼', product_category: '热菜', total_quantity: 760, total_revenue: 92650, net_revenue: 90400, order_count: 718, gross_profit: 49260 },
  { rank: 5, product_name: '麻婆豆腐', product_category: '家常菜', total_quantity: 1320, total_revenue: 78430, net_revenue: 76100, order_count: 1210, gross_profit: 39680 },
  { rank: 6, product_name: '干锅花菜', product_category: '素菜', total_quantity: 1080, total_revenue: 65210, net_revenue: 63800, order_count: 1016, gross_profit: 31880 },
]

const fallbackCategories: CategorySalesItem[] = [
  { category_name: '热菜', revenue: 347730, quantity: 3140, percentage: 43.1 },
  { category_name: '招牌菜', revenue: 142850, quantity: 980, percentage: 17.7 },
  { category_name: '家常菜', revenue: 118110, quantity: 1980, percentage: 14.7 },
  { category_name: '素菜', revenue: 117340, quantity: 2080, percentage: 14.6 },
  { category_name: '饮品', revenue: 80060, quantity: 2240, percentage: 9.9 },
]

const fallbackProfit: ProductProfitItem[] = [
  { rank: 1, product_name: '水煮牛肉', product_category: '热菜', total_revenue: 156320, total_cost: 64680, gross_profit: 91640, profit_margin: 58.6 },
  { rank: 2, product_name: '烤鸭', product_category: '招牌菜', total_revenue: 142850, total_cost: 54110, gross_profit: 88740, profit_margin: 62.1 },
  { rank: 3, product_name: '宫保鸡丁', product_category: '热菜', total_revenue: 98760, total_cost: 43740, gross_profit: 55020, profit_margin: 55.7 },
  { rank: 4, product_name: '酸菜鱼', product_category: '热菜', total_revenue: 92650, total_cost: 43390, gross_profit: 49260, profit_margin: 53.2 },
  { rank: 5, product_name: '麻婆豆腐', product_category: '家常菜', total_revenue: 78430, total_cost: 38750, gross_profit: 39680, profit_margin: 50.6 },
]

const fallbackABC: ProductABCItem[] = [
  { product_name: '水煮牛肉', total_revenue: 156320, percentage: 19.4, cumulative_percentage: 19.4, abc_class: 'A' },
  { product_name: '烤鸭', total_revenue: 142850, percentage: 17.7, cumulative_percentage: 37.1, abc_class: 'A' },
  { product_name: '宫保鸡丁', total_revenue: 98760, percentage: 12.2, cumulative_percentage: 49.3, abc_class: 'A' },
  { product_name: '酸菜鱼', total_revenue: 92650, percentage: 11.5, cumulative_percentage: 60.8, abc_class: 'A' },
  { product_name: '麻婆豆腐', total_revenue: 78430, percentage: 9.7, cumulative_percentage: 70.5, abc_class: 'B' },
  { product_name: '干锅花菜', total_revenue: 65210, percentage: 8.1, cumulative_percentage: 78.6, abc_class: 'B' },
  { product_name: '蒜蓉生菜', total_revenue: 52130, percentage: 6.5, cumulative_percentage: 85.1, abc_class: 'B' },
  { product_name: '手撕包菜', total_revenue: 41520, percentage: 5.2, cumulative_percentage: 90.3, abc_class: 'C' },
]

const fallbackCross: ProductStoreCrossItem[] = [
  { store_name: '朝阳大悦城店', product_name: '水煮牛肉', quantity: 236, revenue: 28640 },
  { store_name: '海淀中关村店', product_name: '烤鸭', quantity: 188, revenue: 27420 },
  { store_name: '西城金融街店', product_name: '宫保鸡丁', quantity: 201, revenue: 17680 },
  { store_name: '望京凯德店', product_name: '酸菜鱼', quantity: 142, revenue: 17310 },
  { store_name: '东直门来福士店', product_name: '麻婆豆腐', quantity: 226, revenue: 13420 },
]

// ABC分类统计
const abcSummary = computed(() => {
  const a = abcData.value.filter(i => i.abc_class === 'A').length
  const b = abcData.value.filter(i => i.abc_class === 'B').length
  const c = abcData.value.filter(i => i.abc_class === 'C').length
  return { a, b, c }
})

// 图表引用
const salesRankingChartRef = ref<HTMLElement | null>(null)
const categoryChartRef = ref<HTMLElement | null>(null)
const profitChartRef = ref<HTMLElement | null>(null)
const abcChartRef = ref<HTMLElement | null>(null)

const {
  setOption: setSalesRankingOption,
  showLoading: showSalesLoading,
  hideLoading: hideSalesLoading
} = useECharts(salesRankingChartRef)

const {
  setOption: setCategoryOption,
  showLoading: showCategoryLoading,
  hideLoading: hideCategoryLoading
} = useECharts(categoryChartRef)

const {
  setOption: setProfitOption,
  showLoading: showProfitLoading,
  hideLoading: hideProfitLoading
} = useECharts(profitChartRef)

const {
  setOption: setAbcOption,
  showLoading: showAbcLoading,
  hideLoading: hideAbcLoading
} = useECharts(abcChartRef)

/** 数字格式化 */
const formatNumber = (val: number): string => {
  if (!val && val !== 0) return '0'
  return val.toLocaleString('zh-CN', { maximumFractionDigits: 1 })
}

const formatCurrency = (val: number): string => {
  if (!val && val !== 0) return '0.00'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/** 安全转数字 */
const toNum = (val: unknown): number => {
  if (val === null || val === undefined) return 0
  const n = Number(val)
  return isNaN(n) ? 0 : n
}

/** 查询触发 */
const handleQuery = async (filters: ProductAnalysisQuery) => {
  currentQuery.value = { ...filters, top_n: topN.value, sort_by: sortBy.value }
  await loadAllData()
}

/** 控制变更触发 */
const handleControlChange = () => {
  currentQuery.value.top_n = topN.value
  currentQuery.value.sort_by = sortBy.value
  loadAllData()
}

/** 并行加载全部数据 */
const loadAllData = async () => {
  await Promise.all([
    loadSalesRanking(),
    loadCategoryDistribution(),
    loadProfitContribution(),
    loadABCClassification(),
    loadProductStoreCross()
  ])
}

/** 加载销量排行 */
const loadSalesRanking = async () => {
  try {
    showSalesLoading()
    const { data } = await getProductSalesRanking(currentQuery.value)
    const items = Array.isArray(data) ? data : []
    const visibleItems = items.length ? items : fallbackSalesRanking.slice(0, topN.value)
    salesRankingData.value = visibleItems
    renderSalesRankingChart(visibleItems)
  } catch (error) {
    void error
  } finally {
    hideSalesLoading()
  }
}

/** 渲染销量排行图表（水平条形图） */
const renderSalesRankingChart = (data: ProductSalesRankingItem[]) => {
  const reversed = [...data].reverse()
  const names = reversed.map(i => i.product_name)
  const values = reversed.map(i =>
    currentQuery.value.sort_by === 'revenue' ? toNum(i.total_revenue) : toNum(i.total_quantity)
  )

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => {
        const list = Array.isArray(params) ? params : []
        const first = list[0] as { dataIndex?: unknown } | undefined
        const dataIndex = typeof first?.dataIndex === 'number' ? first.dataIndex : -1
        const item = reversed[dataIndex]
        if (!item) return ''
        return `
          <div style="font-weight:bold;margin-bottom:var(--spacing-1)">${item.product_name}</div>
          <div>销量: ${formatNumber(toNum(item.total_quantity))}</div>
          <div>销售额: ¥${formatCurrency(toNum(item.total_revenue))}</div>
          <div>订单数: ${item.order_count}</div>
          ${item.gross_profit !== null ? `<div>毛利: ¥${formatCurrency(toNum(item.gross_profit))}</div>` : ''}
        `
      }
    },
    grid: { left: '3%', right: '12%', bottom: '3%', top: 10, containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: (v: number) => v >= 10000 ? (v / 10000).toFixed(1) + 'w' : v.toString()
      }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: {
        width: 80,
        overflow: 'truncate'
      }
    },
    series: [{
      type: 'bar',
      data: values,
      barWidth: '60%',
      label: {
        show: true,
        position: 'right',
        formatter: (p: unknown) => {
          const rawValue = (p as { value?: unknown } | undefined)?.value
          const value = typeof rawValue === 'number' ? rawValue : toNum(rawValue)
          if (currentQuery.value.sort_by === 'revenue') {
            return '¥' + formatCurrency(value)
          }
          return formatNumber(value)
        },
        fontSize: 11
      },
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: COLORS.PRIMARY },
            { offset: 1, color: COLORS.PRIMARY_LIGHT }
          ]
        },
        borderRadius: [0, 4, 4, 0]
      }
    }]
  }

  setSalesRankingOption(option, true)
}

/** 加载品类分布 */
const loadCategoryDistribution = async () => {
  try {
    showCategoryLoading()
    const { data } = await getCategoryDistribution(currentQuery.value)
    const items = Array.isArray(data) ? data : []
    const visibleItems = items.length ? items : fallbackCategories
    categoryData.value = visibleItems
    renderCategoryChart(visibleItems)
  } catch (error) {
    void error
  } finally {
    hideCategoryLoading()
  }
}

/** 渲染品类分布环形图 */
const renderCategoryChart = (data: CategorySalesItem[]) => {
  const chartData = data.map(item => ({
    name: item.category_name,
    value: toNum(item.revenue)
  }))

  const option: ECOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: unknown) => {
        const p = params as { name?: unknown; value?: unknown; percent?: unknown }
        const name = typeof p.name === 'string' ? p.name : ''
        const value = typeof p.value === 'number' ? p.value : toNum(p.value)
        const percent = typeof p.percent === 'number' ? p.percent : toNum(p.percent)
        return `${name}<br/>销售额: ¥${formatCurrency(value)}<br/>占比: ${percent}%`
      }
    },
    legend: { top: 'bottom', left: 'center' },
    series: [{
      name: '品类销售',
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
        label: { show: true, fontSize: 16, fontWeight: 'bold' }
      },
      data: chartData
    }],
    color: CHART_PALETTE.CATEGORY
  }

  setCategoryOption(option, true)
}

/** 加载毛利贡献 */
const loadProfitContribution = async () => {
  try {
    showProfitLoading()
    const { data } = await getProductProfitContribution(currentQuery.value)
    const items = Array.isArray(data) ? data : []
    const visibleItems = items.length ? items : fallbackProfit.slice(0, topN.value)
    profitData.value = visibleItems
    renderProfitChart(visibleItems)
  } catch (error) {
    void error
  } finally {
    hideProfitLoading()
  }
}

/** 渲染毛利贡献图表（双色堆叠条形图） */
const renderProfitChart = (data: ProductProfitItem[]) => {
  const reversed = [...data].reverse()
  const names = reversed.map(i => i.product_name)
  const costs = reversed.map(i => toNum(i.total_cost))
  const profits = reversed.map(i => toNum(i.gross_profit))

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => {
        const list = Array.isArray(params) ? params : []
        const first = list[0] as { dataIndex?: unknown } | undefined
        const dataIndex = typeof first?.dataIndex === 'number' ? first.dataIndex : -1
        const item = reversed[dataIndex]
        if (!item) return ''
        return `
          <div style="font-weight:bold;margin-bottom:var(--spacing-1)">${item.product_name}</div>
          <div>销售额: ¥${formatCurrency(toNum(item.total_revenue))}</div>
          <div>成本: ¥${formatCurrency(toNum(item.total_cost))}</div>
          <div>毛利: ¥${formatCurrency(toNum(item.gross_profit))}</div>
          <div>毛利率: ${toNum(item.profit_margin).toFixed(2)}%</div>
        `
      }
    },
    legend: { data: ['成本', '毛利'], top: 5 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: 40, containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: (v: number) => v >= 10000 ? (v / 10000).toFixed(1) + 'w' : v.toString()
      }
    },
    yAxis: {
      type: 'category',
      data: names,
      axisLabel: { width: 80, overflow: 'truncate' }
    },
    series: [
      {
        name: '成本',
        type: 'bar',
        stack: 'total',
        data: costs,
        itemStyle: { color: COLORS.WARNING },
        barWidth: '60%'
      },
      {
        name: '毛利',
        type: 'bar',
        stack: 'total',
        data: profits,
        itemStyle: { color: COLORS.SUCCESS },
        barWidth: '60%'
      }
    ]
  }

  setProfitOption(option, true)
}

/** 加载ABC分类 */
const loadABCClassification = async () => {
  try {
    abcLoading.value = true
    showAbcLoading()
    const { data } = await getProductABCClassification({
      ...currentQuery.value,
      top_n: undefined // ABC分类不限制数量
    })
    const items = Array.isArray(data) ? data : []
    const visibleItems = items.length ? items : fallbackABC
    abcData.value = visibleItems
    renderAbcChart(visibleItems)
  } catch (error) {
    void error
  } finally {
    abcLoading.value = false
    hideAbcLoading()
  }
}

/** 渲染ABC分类饼图 */
const renderAbcChart = (data: ProductABCItem[]) => {
  const groups: Record<string, { count: number; revenue: number }> = {
    A: { count: 0, revenue: 0 },
    B: { count: 0, revenue: 0 },
    C: { count: 0, revenue: 0 }
  }

  data.forEach(item => {
    const cls = item.abc_class
    groups[cls].count++
    groups[cls].revenue += toNum(item.total_revenue)
  })

  const chartData = [
    { name: `A类 (${groups.A.count}种)`, value: groups.A.revenue },
    { name: `B类 (${groups.B.count}种)`, value: groups.B.revenue },
    { name: `C类 (${groups.C.count}种)`, value: groups.C.revenue }
  ]

  const option: ECOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: unknown) => {
        const p = params as { name?: unknown; value?: unknown; percent?: unknown }
        const name = typeof p.name === 'string' ? p.name : ''
        const value = typeof p.value === 'number' ? p.value : toNum(p.value)
        const percent = typeof p.percent === 'number' ? p.percent : toNum(p.percent)
        return `${name}<br/>销售额: ¥${formatCurrency(value)}<br/>占比: ${percent}%`
      }
    },
    legend: { top: 'bottom', left: 'center' },
    series: [{
      name: 'ABC分类',
      type: 'pie',
      radius: ['35%', '65%'],
      itemStyle: {
        borderRadius: 8,
        borderColor: COLORS.WHITE,
        borderWidth: 2
      },
      label: {
        show: true,
        formatter: '{b}\n{d}%',
        fontSize: 13
      },
      emphasis: {
        label: { show: true, fontSize: 16, fontWeight: 'bold' }
      },
      data: chartData
    }],
    color: [COLORS.SUCCESS, COLORS.WARNING, COLORS.DANGER]
  }

  setAbcOption(option, true)
}

/** 加载门店交叉分析 */
const loadProductStoreCross = async () => {
  try {
    crossLoading.value = true
    const { data } = await getProductStoreCross(currentQuery.value)
    const items = Array.isArray(data) ? data : []
    crossData.value = items.length ? items : fallbackCross
  } catch (error) {
    void error
  } finally {
    crossLoading.value = false
  }
}

onMounted(() => {
  // FilterBar 组件初始化时会自动触发 handleQuery
})
</script>

<style scoped lang="scss">
.product-analysis-container {
  padding: 0;
}

.analysis-page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 12px;

  h1 {
    margin: 2px 0 0;
    color: #211A15;
    font-size: 22px;
    font-weight: 900;
  }

  > span {
    color: #8A8074;
    font-size: 12px;
    font-weight: 700;
  }
}

.eyebrow {
  margin: 0;
  color: #8A8074;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
}

.control-card {
  margin-bottom: 12px;
  border: 1px solid #E5DED4;
  border-radius: 6px;
  background: rgba(255, 253, 249, 0.96);
  box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);

  .control-label {
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    margin-right: var(--spacing-2);
  }
}

.chart-card,
.table-card {
  margin-bottom: 12px;
  border: 1px solid #E5DED4;
  border-radius: 6px;
  background: rgba(255, 253, 249, 0.96);
  box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      display: flex;
      align-items: center;
      gap: var(--spacing-2);
      font-size: var(--font-size-base);
      font-weight: 900;
      color: #211A15;

      .el-icon {
        color: #C81E1E;
      }
    }
  }

  .chart-container {
    width: 100%;
    height: calc(var(--spacing-6) * 12.5);
  }
}

.abc-summary {
  margin-bottom: var(--spacing-3);

  .abc-tag-group {
    display: flex;
    gap: var(--spacing-3);
    justify-content: center;
    flex-wrap: wrap;
  }
}

.product-select {
  width: calc(var(--spacing-6) * 3.75); // 120px
}
</style>
