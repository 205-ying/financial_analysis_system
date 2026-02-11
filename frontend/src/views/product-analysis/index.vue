<template>
  <div class="product-analysis-container">
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
          <el-select v-model="topN" size="small" style="width: 120px" @change="handleControlChange">
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
            <span style="color: #409eff; font-weight: 600">¥{{ formatCurrency(row.revenue) }}</span>
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
            <span :style="{ color: row.cumulative_percentage <= 70 ? '#67c23a' : row.cumulative_percentage <= 90 ? '#e6a23c' : '#f56c6c' }">
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
const toNum = (val: any): number => {
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
    salesRankingData.value = items
    renderSalesRankingChart(items)
  } catch (error) {
    console.error('加载销量排行失败:', error)
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
      formatter: (params: any) => {
        const item = reversed[params[0].dataIndex]
        if (!item) return ''
        return `
          <div style="font-weight:bold;margin-bottom:5px">${item.product_name}</div>
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
        formatter: (p: any) => {
          if (currentQuery.value.sort_by === 'revenue') {
            return '¥' + formatCurrency(p.value)
          }
          return formatNumber(p.value)
        },
        fontSize: 11
      },
      itemStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 1, y2: 0,
          colorStops: [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#79bbff' }
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
    categoryData.value = items
    renderCategoryChart(items)
  } catch (error) {
    console.error('加载品类分布失败:', error)
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
      formatter: (params: any) => {
        return `${params.name}<br/>销售额: ¥${formatCurrency(params.value)}<br/>占比: ${params.percent}%`
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
        borderColor: '#fff',
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
    color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
  }

  setCategoryOption(option, true)
}

/** 加载毛利贡献 */
const loadProfitContribution = async () => {
  try {
    showProfitLoading()
    const { data } = await getProductProfitContribution(currentQuery.value)
    const items = Array.isArray(data) ? data : []
    profitData.value = items
    renderProfitChart(items)
  } catch (error) {
    console.error('加载毛利贡献失败:', error)
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
      formatter: (params: any) => {
        const item = reversed[params[0].dataIndex]
        if (!item) return ''
        return `
          <div style="font-weight:bold;margin-bottom:5px">${item.product_name}</div>
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
        itemStyle: { color: '#fac858' },
        barWidth: '60%'
      },
      {
        name: '毛利',
        type: 'bar',
        stack: 'total',
        data: profits,
        itemStyle: { color: '#91cc75' },
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
    abcData.value = items
    renderAbcChart(items)
  } catch (error) {
    console.error('加载ABC分类失败:', error)
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
      formatter: (params: any) => {
        return `${params.name}<br/>销售额: ¥${formatCurrency(params.value)}<br/>占比: ${params.percent}%`
      }
    },
    legend: { top: 'bottom', left: 'center' },
    series: [{
      name: 'ABC分类',
      type: 'pie',
      radius: ['35%', '65%'],
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
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
    color: ['#67c23a', '#e6a23c', '#f56c6c']
  }

  setAbcOption(option, true)
}

/** 加载门店交叉分析 */
const loadProductStoreCross = async () => {
  try {
    crossLoading.value = true
    const { data } = await getProductStoreCross(currentQuery.value)
    crossData.value = Array.isArray(data) ? data : []
  } catch (error) {
    console.error('加载门店交叉分析失败:', error)
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

.control-card {
  margin-bottom: 20px;

  .control-label {
    font-size: 14px;
    color: #606266;
    margin-right: 8px;
  }
}

.chart-card,
.table-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
    }
  }

  .chart-container {
    width: 100%;
    height: 400px;
  }
}

.abc-summary {
  margin-bottom: 12px;

  .abc-tag-group {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>
