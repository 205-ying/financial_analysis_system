<template>
  <div class="comparison-container">
    <!-- 筛选条件 -->
    <el-card shadow="never" class="filter-card">
      <el-form :model="filterForm" :inline="true" label-width="80px">
        <el-form-item label="门店">
          <StoreSelect v-model="filterForm.store_id" width="200px" />
        </el-form-item>

        <el-form-item label="当期范围">
          <el-date-picker
            v-model="currentDateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            :shortcuts="dateShortcuts"
            style="width: 360px"
          />
        </el-form-item>

        <el-form-item label="对比方式">
          <el-radio-group v-model="filterForm.compare_type" @change="handleCompareTypeChange">
            <el-radio-button value="yoy">同比(去年)</el-radio-button>
            <el-radio-button value="mom">环比(上月)</el-radio-button>
            <el-radio-button value="custom">自定义</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="filterForm.compare_type === 'custom'" label="对比期">
          <el-date-picker
            v-model="compareDateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 360px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 核心指标对比卡片 -->
    <el-row :gutter="16" class="metric-cards">
      <el-col v-for="card in metricCards" :key="card.key" :xs="12" :sm="6">
        <el-card shadow="never" class="metric-card">
          <div class="metric-label">{{ card.label }}</div>
          <div class="metric-value">{{ formatNumber(card.current) }}</div>
          <div class="metric-compare">
            <span class="previous">对比期: {{ formatNumber(card.previous) }}</span>
            <span
              class="growth"
              :class="{
                'growth-up': card.growth !== null && card.growth > 0,
                'growth-down': card.growth !== null && card.growth < 0,
                'growth-flat': card.growth === null || card.growth === 0
              }"
            >
              <template v-if="card.growth !== null">
                <el-icon v-if="card.growth > 0"><Top /></el-icon>
                <el-icon v-else-if="card.growth < 0"><Bottom /></el-icon>
                {{ Math.abs(card.growth) }}%
              </template>
              <template v-else>--</template>
            </span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 趋势对比图表 -->
    <el-card shadow="never" class="chart-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><TrendCharts /></el-icon>
            趋势对比
          </span>
          <el-radio-group v-model="trendMetric" size="small" @change="fetchTrendData">
            <el-radio-button value="revenue">营收</el-radio-button>
            <el-radio-button value="operating_profit">利润</el-radio-button>
            <el-radio-button value="order_count">订单数</el-radio-button>
            <el-radio-button value="avg_order_value">客单价</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="trendChartRef" class="chart-container"></div>
    </el-card>

    <!-- 门店对比表格 -->
    <el-card shadow="never" class="table-card">
      <template #header>
        <div class="card-header">
          <span class="title">
            <el-icon><OfficeBuilding /></el-icon>
            门店对比明细
          </span>
          <span v-if="periodInfo" class="period-info">
            当期: {{ periodInfo.current }} | 对比期: {{ periodInfo.previous }}
          </span>
        </div>
      </template>
      <el-table
        v-loading="storeLoading"
        :data="storeData"
        border
        stripe
        style="width: 100%"
      >
        <el-table-column prop="store_name" label="门店" min-width="120" fixed />
        <el-table-column label="营收" align="center">
          <el-table-column prop="current_revenue" label="当期" min-width="100" align="right">
            <template #default="{ row }">{{ formatNumber(row.current_revenue) }}</template>
          </el-table-column>
          <el-table-column prop="previous_revenue" label="对比期" min-width="100" align="right">
            <template #default="{ row }">{{ formatNumber(row.previous_revenue) }}</template>
          </el-table-column>
          <el-table-column prop="revenue_growth_rate" label="增长率" min-width="100" align="center">
            <template #default="{ row }">
              <growth-tag :value="row.revenue_growth_rate" />
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="利润" align="center">
          <el-table-column prop="current_profit" label="当期" min-width="100" align="right">
            <template #default="{ row }">{{ formatNumber(row.current_profit) }}</template>
          </el-table-column>
          <el-table-column prop="previous_profit" label="对比期" min-width="100" align="right">
            <template #default="{ row }">{{ formatNumber(row.previous_profit) }}</template>
          </el-table-column>
          <el-table-column prop="profit_growth_rate" label="增长率" min-width="100" align="center">
            <template #default="{ row }">
              <growth-tag :value="row.profit_growth_rate" />
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="订单数" align="center">
          <el-table-column prop="current_order_count" label="当期" min-width="80" align="right" />
          <el-table-column prop="previous_order_count" label="对比期" min-width="80" align="right" />
          <el-table-column prop="order_growth_rate" label="增长率" min-width="100" align="center">
            <template #default="{ row }">
              <growth-tag :value="row.order_growth_rate" />
            </template>
          </el-table-column>
        </el-table-column>
        <el-table-column label="客单价" align="center">
          <el-table-column prop="current_avg_order_value" label="当期" min-width="80" align="right">
            <template #default="{ row }">{{ formatNumber(row.current_avg_order_value) }}</template>
          </el-table-column>
          <el-table-column prop="previous_avg_order_value" label="对比期" min-width="80" align="right">
            <template #default="{ row }">{{ formatNumber(row.previous_avg_order_value) }}</template>
          </el-table-column>
          <el-table-column prop="avg_order_value_growth_rate" label="增长率" min-width="100" align="center">
            <template #default="{ row }">
              <growth-tag :value="row.avg_order_value_growth_rate" />
            </template>
          </el-table-column>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Top, Bottom, TrendCharts, OfficeBuilding } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

import StoreSelect from '@/components/StoreSelect.vue'
import { useECharts } from '@/composables/useECharts'
import {
  getPeriodComparison,
  getTrendComparison,
  getStoreComparison
} from '@/api/comparison'
import type {
  ComparisonQuery,
  MetricComparison,
  TrendComparisonResponse,
  StoreComparisonItem
} from '@/types'

// ───────────── GrowthTag 子组件 (内联) ─────────────
const GrowthTag = {
  name: 'GrowthTag',
  props: {
    value: { type: Number, default: null }
  },
  template: `
    <span v-if="value !== null && value !== undefined"
          :style="{ color: value > 0 ? '#67c23a' : value < 0 ? '#f56c6c' : '#909399', fontWeight: 'bold' }">
      {{ value > 0 ? '↑' : value < 0 ? '↓' : '' }}{{ Math.abs(value) }}%
    </span>
    <span v-else style="color: #909399">--</span>
  `
}

// ───────────── 筛选状态 ─────────────
const filterForm = reactive<{
  store_id: number | undefined
  compare_type: 'yoy' | 'mom' | 'custom'
}>({
  store_id: undefined,
  compare_type: 'yoy'
})

const currentDateRange = ref<[string, string]>()
const compareDateRange = ref<[string, string]>()

const dateShortcuts = [
  {
    text: '最近一周',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 7)
      return [start, end]
    }
  },
  {
    text: '最近一个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 30)
      return [start, end]
    }
  },
  {
    text: '最近三个月',
    value: () => {
      const end = new Date()
      const start = new Date()
      start.setTime(start.getTime() - 3600 * 1000 * 24 * 90)
      return [start, end]
    }
  }
]

// ───────────── 核心指标 ─────────────
interface MetricCard {
  key: string
  label: string
  current: number
  previous: number
  growth: number | null
}

const metricCards = ref<MetricCard[]>([
  { key: 'revenue', label: '营业收入', current: 0, previous: 0, growth: null },
  { key: 'operating_profit', label: '营业利润', current: 0, previous: 0, growth: null },
  { key: 'order_count', label: '订单数', current: 0, previous: 0, growth: null },
  { key: 'avg_order_value', label: '客单价', current: 0, previous: 0, growth: null }
])

const periodInfo = ref<{ current: string; previous: string } | null>(null)

// ───────────── 趋势图表 ─────────────
const trendMetric = ref('revenue')
const trendChartRef = ref<HTMLElement | null>(null)
const { setOption: setTrendOption, showLoading: showTrendLoading, hideLoading: hideTrendLoading } =
  useECharts(trendChartRef)

// ───────────── 门店数据 ─────────────
const storeLoading = ref(false)
const storeData = ref<StoreComparisonItem[]>([])

// ───────────── 工具函数 ─────────────
function formatNumber(val: number | null | undefined): string {
  if (val === null || val === undefined) return '--'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function buildQueryParams(): ComparisonQuery | null {
  if (!currentDateRange.value || currentDateRange.value.length < 2) {
    ElMessage.warning('请选择当期日期范围')
    return null
  }
  const params: ComparisonQuery = {
    start_date: currentDateRange.value[0],
    end_date: currentDateRange.value[1],
    compare_type: filterForm.compare_type,
    store_id: filterForm.store_id
  }
  if (filterForm.compare_type === 'custom') {
    if (!compareDateRange.value || compareDateRange.value.length < 2) {
      ElMessage.warning('自定义对比模式下请选择对比期日期范围')
      return null
    }
    params.compare_start_date = compareDateRange.value[0]
    params.compare_end_date = compareDateRange.value[1]
  }
  return params
}

// ───────────── 数据获取 ─────────────
async function fetchPeriodData() {
  const params = buildQueryParams()
  if (!params) return

  try {
    const res = await getPeriodComparison(params)
    if (res.code === 0 && res.data) {
      const { metrics, current_period, previous_period } = res.data
      periodInfo.value = { current: current_period, previous: previous_period }

      // 更新4张核心卡片
      const cardKeys = ['revenue', 'operating_profit', 'order_count', 'avg_order_value']
      cardKeys.forEach((key, idx) => {
        const found = metrics.find((m: MetricComparison) => m.metric_name === key)
        if (found) {
          metricCards.value[idx] = {
            key,
            label: found.metric_label,
            current: found.current_value,
            previous: found.previous_value,
            growth: found.growth_rate
          }
        }
      })
    }
  } catch {
    ElMessage.error('获取期间对比数据失败')
  }
}

async function fetchTrendData() {
  const params = buildQueryParams()
  if (!params) return

  showTrendLoading()
  try {
    const res = await getTrendComparison({ ...params, metric: trendMetric.value })
    if (res.code === 0 && res.data) {
      renderTrendChart(res.data)
    }
  } catch {
    ElMessage.error('获取趋势对比数据失败')
  } finally {
    hideTrendLoading()
  }
}

async function fetchStoreData() {
  const params = buildQueryParams()
  if (!params) return

  storeLoading.value = true
  try {
    const res = await getStoreComparison(params)
    if (res.code === 0 && res.data) {
      storeData.value = res.data
    }
  } catch {
    ElMessage.error('获取门店对比数据失败')
  } finally {
    storeLoading.value = false
  }
}

// ───────────── 图表渲染 ─────────────
function renderTrendChart(data: TrendComparisonResponse) {
  const labels = data.data.map(d => d.date_label)
  const currentValues = data.data.map(d => d.current_value)
  const previousValues = data.data.map(d => d.previous_value)

  setTrendOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: [`当期 (${data.current_period})`, `对比期 (${data.previous_period})`],
      bottom: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '14%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLabel: {
        rotate: labels.length > 15 ? 45 : 0,
        fontSize: 11
      }
    },
    yAxis: {
      type: 'value',
      name: data.metric_label
    },
    series: [
      {
        name: `当期 (${data.current_period})`,
        type: 'line',
        data: currentValues,
        smooth: true,
        lineStyle: { width: 2 },
        itemStyle: { color: '#409eff' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64,158,255,0.3)' },
              { offset: 1, color: 'rgba(64,158,255,0.05)' }
            ]
          }
        }
      },
      {
        name: `对比期 (${data.previous_period})`,
        type: 'line',
        data: previousValues,
        smooth: true,
        lineStyle: { width: 2, type: 'dashed' },
        itemStyle: { color: '#e6a23c' }
      }
    ]
  }, true)
}

// ───────────── 事件处理 ─────────────
function handleQuery() {
  fetchPeriodData()
  fetchTrendData()
  fetchStoreData()
}

function handleReset() {
  filterForm.store_id = undefined
  filterForm.compare_type = 'yoy'
  compareDateRange.value = undefined

  const end = dayjs()
  const start = end.subtract(30, 'day')
  currentDateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]

  handleQuery()
}

function handleCompareTypeChange() {
  if (filterForm.compare_type !== 'custom') {
    compareDateRange.value = undefined
  }
}

// ───────────── 初始化 ─────────────
onMounted(() => {
  const end = dayjs()
  const start = end.subtract(30, 'day')
  currentDateRange.value = [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')]

  handleQuery()
})
</script>

<style scoped lang="scss">
.comparison-container {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;

  :deep(.el-card__body) {
    padding: 20px;
  }

  .el-form {
    margin: 0;
  }
}

.metric-cards {
  margin-bottom: 20px;
}

.metric-card {
  text-align: center;
  transition: box-shadow 0.3s;

  &:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.12);
  }

  .metric-label {
    font-size: 14px;
    color: #909399;
    margin-bottom: 8px;
  }

  .metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 8px;
  }

  .metric-compare {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    font-size: 13px;

    .previous {
      color: #909399;
    }

    .growth {
      font-weight: bold;
      display: inline-flex;
      align-items: center;
      gap: 2px;
    }

    .growth-up {
      color: #67c23a;
    }

    .growth-down {
      color: #f56c6c;
    }

    .growth-flat {
      color: #909399;
    }
  }
}

.chart-card,
.table-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  .title {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 16px;
    font-weight: bold;
  }

  .period-info {
    font-size: 12px;
    color: #909399;
  }
}

.chart-container {
  width: 100%;
  height: 400px;
}
</style>
