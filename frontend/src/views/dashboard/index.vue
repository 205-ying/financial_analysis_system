<template>
  <div class="dashboard-container">
    <!-- 筛选条件 -->
    <filter-bar @query="handleQuery" ref="filterBarRef">
      <template #extra-buttons>
        <el-button
          type="success"
          :icon="RefreshRight"
          v-permission="'kpi:rebuild'"
          @click="handleRebuildKPI"
          :loading="rebuildLoading"
        >
          重建KPI
        </el-button>
      </template>
    </filter-bar>

    <!-- KPI 卡片 -->
    <el-row :gutter="20" class="kpi-cards">
      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="kpi-card revenue-card" shadow="hover">
          <div class="kpi-icon">
            <el-icon :size="40"><Money /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-label">总营收</div>
            <div class="kpi-value">¥{{ formatNumber(kpiSummary.total_revenue) }}</div>
            <div class="kpi-extra">订单数: {{ kpiSummary.order_count }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="kpi-card cost-card" shadow="hover">
          <div class="kpi-icon">
            <el-icon :size="40"><WalletFilled /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-label">总成本</div>
            <div class="kpi-value">¥{{ formatNumber(kpiSummary.total_cost) }}</div>
            <div class="kpi-extra">费用数: {{ kpiSummary.expense_count }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="kpi-card profit-card" shadow="hover">
          <div class="kpi-icon">
            <el-icon :size="40"><TrendCharts /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-label">总利润</div>
            <div class="kpi-value">¥{{ formatNumber(kpiSummary.total_profit) }}</div>
            <div class="kpi-extra">门店数: {{ kpiSummary.store_count }}</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :lg="6">
        <el-card class="kpi-card rate-card" shadow="hover">
          <div class="kpi-icon">
            <el-icon :size="40"><DataAnalysis /></el-icon>
          </div>
          <div class="kpi-content">
            <div class="kpi-label">利润率</div>
            <div class="kpi-value">{{ formatPercent(kpiSummary.profit_rate) }}%</div>
            <div class="kpi-extra">{{ kpiSummary.date_range?.start_date }} ~ {{ kpiSummary.date_range?.end_date }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势折线图 -->
    <el-card class="chart-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">营收趋势分析</span>
          <el-radio-group v-model="granularity" size="small" @change="handleGranularityChange">
            <el-radio-button label="day">按日</el-radio-button>
            <el-radio-button label="week">按周</el-radio-button>
            <el-radio-button label="month">按月</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="trendChartRef" class="chart-container"></div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Money, WalletFilled, TrendCharts, DataAnalysis, RefreshRight } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { FilterBar } from '@/components'
import { useECharts, type ECOption } from '@/composables/useECharts'
import { getKPISummary, getKPITrend, rebuildKPI } from '@/api/kpi'
import type { KPISummary, KPITrendItem, KPIQuery } from '@/types'

// 筛选栏引用
const filterBarRef = ref()

// KPI 汇总数据
const kpiSummary = reactive<KPISummary>({
  total_revenue: 0,
  total_cost: 0,
  total_profit: 0,
  profit_rate: 0,
  order_count: 0,
  expense_count: 0,
  store_count: 0,
  date_range: {
    start_date: '',
    end_date: ''
  }
})

// 趋势数据
const trendData = ref<KPITrendItem[]>([])

// 粒度
const granularity = ref<'day' | 'week' | 'month'>('day')

// 重建 KPI 加载状态
const rebuildLoading = ref(false)

// 当前查询参数
const currentQuery = ref<KPIQuery>({})

// 趋势图表
const trendChartRef = ref<HTMLElement | null>(null)
const { setOption: setTrendOption, showLoading: showTrendLoading, hideLoading: hideTrendLoading } = useECharts(trendChartRef)

/**
 * 格式化数字
 */
const formatNumber = (value: number): string => {
  if (value === 0) return '0'
  if (!value) return '0'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/**
 * 格式化百分比
 */
const formatPercent = (value: number): string => {
  if (value === 0) return '0.00'
  if (!value) return '0.00'
  return (value * 100).toFixed(2)
}

/**
 * 处理查询
 */
const handleQuery = async (filters: KPIQuery) => {
  currentQuery.value = { ...filters, granularity: granularity.value }
  await Promise.all([loadKPISummary(), loadKPITrend()])
}

/**
 * 处理粒度改变
 */
const handleGranularityChange = () => {
  currentQuery.value.granularity = granularity.value
  loadKPITrend()
}

/**
 * 加载 KPI 汇总数据
 */
const loadKPISummary = async () => {
  try {
    const { data } = await getKPISummary(currentQuery.value)
    Object.assign(kpiSummary, data)
  } catch (error) {
    console.error('加载 KPI 汇总数据失败:', error)
  }
}

/**
 * 加载 KPI 趋势数据
 */
const loadKPITrend = async () => {
  try {
    showTrendLoading()
    const { data } = await getKPITrend(currentQuery.value)
    // 后端返回的是 {items: [], summary: {}}，需要提取 items
    const trendItems = (data as any).items || data
    trendData.value = trendItems
    renderTrendChart(trendItems)
  } catch (error) {
    console.error('加载 KPI 趋势数据失败:', error)
  } finally {
    hideTrendLoading()
  }
}

/**
 * 渲染趋势图表
 */
const renderTrendChart = (data: KPITrendItem[]) => {
  const dates = data.map(item => item.date)
  const revenues = data.map(item => item.revenue)
  const costs = data.map(item => item.cost)
  const profits = data.map(item => item.profit)

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      },
      formatter: (params: any) => {
        let result = `<div style="font-weight: bold; margin-bottom: 5px;">${params[0].axisValue}</div>`
        params.forEach((item: any) => {
          result += `<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 3px;">
            <span>${item.marker}${item.seriesName}:</span>
            <span style="font-weight: bold; margin-left: 20px;">¥${item.value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
          </div>`
        })
        return result
      }
    },
    legend: {
      data: ['营收', '成本', '利润'],
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
      boundaryGap: false,
      data: dates,
      axisLabel: {
        rotate: dates.length > 15 ? 45 : 0
      }
    },
    yAxis: {
      type: 'value',
      name: '金额(元)',
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 10000) {
            return (value / 10000).toFixed(1) + 'w'
          }
          return value.toString()
        }
      }
    },
    series: [
      {
        name: '营收',
        type: 'line',
        data: revenues,
        smooth: true,
        itemStyle: { color: '#67c23a' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
            ]
          }
        }
      },
      {
        name: '成本',
        type: 'line',
        data: costs,
        smooth: true,
        itemStyle: { color: '#e6a23c' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(230, 162, 60, 0.3)' },
              { offset: 1, color: 'rgba(230, 162, 60, 0.05)' }
            ]
          }
        }
      },
      {
        name: '利润',
        type: 'line',
        data: profits,
        smooth: true,
        itemStyle: { color: '#409eff' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        }
      }
    ]
  }

  setTrendOption(option, true)
}

/**
 * 处理重建 KPI
 */
const handleRebuildKPI = async () => {
  try {
    await ElMessageBox.confirm(
      '重建 KPI 会重新计算所选日期范围内的所有 KPI 数据，是否继续？',
      '确认重建',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    rebuildLoading.value = true
    const params = {
      start_date: currentQuery.value.start_date,
      end_date: currentQuery.value.end_date
    }
    const { data } = await rebuildKPI(params)
    ElMessage.success(`重建成功！影响 ${data.rows_affected} 行数据`)
    
    // 重新加载数据
    await handleQuery(currentQuery.value)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('重建 KPI 失败:', error)
    }
  } finally {
    rebuildLoading.value = false
  }
}

onMounted(() => {
  // 初始化时会由 FilterBar 自动触发查询
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 0;
}

.kpi-cards {
  margin-bottom: 20px;

  .kpi-card {
    margin-bottom: 20px;
    transition: transform 0.3s;

    &:hover {
      transform: translateY(-5px);
    }

    :deep(.el-card__body) {
      display: flex;
      align-items: center;
      padding: 24px;
    }

    .kpi-icon {
      width: 80px;
      height: 80px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
      margin-right: 20px;
    }

    .kpi-content {
      flex: 1;

      .kpi-label {
        font-size: 14px;
        color: #909399;
        margin-bottom: 8px;
      }

      .kpi-value {
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 8px;
      }

      .kpi-extra {
        font-size: 12px;
        color: #c0c4cc;
      }
    }

    &.revenue-card {
      .kpi-icon {
        background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
        color: white;
      }

      .kpi-value {
        color: #67c23a;
      }
    }

    &.cost-card {
      .kpi-icon {
        background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
        color: white;
      }

      .kpi-value {
        color: #e6a23c;
      }
    }

    &.profit-card {
      .kpi-icon {
        background: linear-gradient(135deg, #409eff 0%, #79bbff 100%);
        color: white;
      }

      .kpi-value {
        color: #409eff;
      }
    }

    &.rate-card {
      .kpi-icon {
        background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%);
        color: white;
      }

      .kpi-value {
        color: #f56c6c;
      }
    }
  }
}

.chart-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      font-size: 16px;
      font-weight: 600;
    }
  }

  .chart-container {
    width: 100%;
    height: 400px;
  }
}
</style>
