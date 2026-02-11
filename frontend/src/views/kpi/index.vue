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
              <span class="legend-value">￥{{ formatNumber(item.total_amount || item.amount || 0) }}</span>
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
              <el-select v-model="topN" size="small" style="width: 120px" @change="handleTopNChange">
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
            <span style="color: #67c23a; font-weight: 600">¥{{ formatNumber(row.revenue || row.total_revenue || 0) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="成本" width="150" align="right">
          <template #default="{ row }">
            <span style="color: #e6a23c; font-weight: 600">¥{{ formatNumber(row.cost || row.total_cost || 0) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="利润" width="150" align="right">
          <template #default="{ row }">
            <span style="color: #409eff; font-weight: 600">¥{{ formatNumber(row.profit || row.total_profit || 0) }}</span>
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

/**
 * 加载费用分类数据
 */
const loadExpenseCategory = async () => {
  try {
    showCategoryLoading()
    const { data } = await getExpenseCategory(currentQuery.value)
    // 后端返回 {categories: [...], total_amount: xxx}，提取 categories
    const categories = (data as any).categories || data
    expenseCategoryData.value = categories
    renderCategoryChart(categories)
  } catch (error) {
    console.error('加载费用分类数据失败:', error)
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
    value: item.total_amount || item.amount  // 兼容两种字段名
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
          borderColor: '#fff',
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
    color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
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
    // 后端返回 {stores: [...], total_stores: xxx}，提取 stores
    const stores = (data as any).stores || data
    storeRankingData.value = stores
    renderRankingChart(stores)
  } catch (error) {
    console.error('加载门店排名数据失败:', error)
  } finally {
    hideRankingLoading()
  }
}

/**
 * 渲染门店排名图表（柱状图）
 */
const renderRankingChart = (data: any[]) => {
  const storeNames = data.map(item => item.store_name)
  // 后端返回 profit 和 profit_margin，前端可能用 total_profit 和 profit_rate
  const profits = data.map(item => item.profit || item.total_profit || 0)
  const profitRates = data.map(item => (item.profit_margin !== undefined ? item.profit_margin : (item.profit_rate || 0) * 100))

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        let result = `<div style="font-weight: bold; margin-bottom: 5px;">${params[0].axisValue}</div>`
        params.forEach((item: any) => {
          if (item.seriesName === '利润') {
            result += `<div>${item.marker}${item.seriesName}: ¥${item.value.toLocaleString('zh-CN', {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2
            })}</div>`
          } else {
            result += `<div>${item.marker}${item.seriesName}: ${item.value.toFixed(2)}%</div>`
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
              { offset: 0, color: '#409eff' },
              { offset: 1, color: '#79bbff' }
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
        itemStyle: { color: '#67c23a' },
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
  padding: 0;
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

  .chart-legend {
    margin-top: 20px;
    padding: 15px;
    background: #f5f7fa;
    border-radius: 4px;

    .legend-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #e4e7ed;

      &:last-child {
        border-bottom: none;
      }

      .legend-label {
        color: #606266;
        font-weight: 500;
      }

      .legend-value {
        color: #409eff;
        font-weight: 600;
      }

      .legend-percent {
        color: #909399;
      }
    }
  }
}
</style>
