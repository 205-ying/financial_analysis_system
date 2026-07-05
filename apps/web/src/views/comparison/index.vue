<template>
  <div class="comparison-container">
    <section class="analysis-page-head">
      <div>
        <p class="eyebrow">Period Comparison</p>
        <h1>同比环比分析</h1>
      </div>
      <span>当期、对比期和门店增长表现</span>
    </section>

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
            class="date-range-picker"
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
            class="date-range-picker"
          />
        </el-form-item>

        <el-form-item class="filter-actions">
          <div class="action-cluster action-cluster--query">
            <el-button type="primary" :icon="Search" @click="handleQuery">查询</el-button>
            <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          </div>
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
import { h, ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Top, Bottom, TrendCharts, OfficeBuilding } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

import StoreSelect from '@/components/StoreSelect.vue'
import { useECharts } from '@/composables/useECharts'
import { COLORS } from '@/utils/colors'
import { DEMO_PERIOD } from '@/config'
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
  setup(props: { value: number | null }) {
    return () => {
      if (props.value === null || props.value === undefined) {
        return h('span', { style: { color: 'var(--color-text-tertiary)' } }, '--')
      }

      const color =
        props.value > 0
          ? 'var(--color-success)'
          : props.value < 0
            ? 'var(--color-danger)'
            : 'var(--color-text-tertiary)'

      return h(
        'span',
        { style: { color, fontWeight: 'bold' } },
        `${props.value > 0 ? '↑' : props.value < 0 ? '↓' : ''}${Math.abs(props.value)}%`
      )
    }
  }
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
    text: '演示经营月',
    value: () => [dayjs(DEMO_PERIOD.startDate).toDate(), dayjs(DEMO_PERIOD.endDate).toDate()]
  },
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

const fallbackMetrics: MetricComparison[] = [
  { metric_name: 'revenue', metric_label: '营业收入', current_value: 2485630, previous_value: 2186900, difference: 298730, growth_rate: 13.66 },
  { metric_name: 'operating_profit', metric_label: '营业利润', current_value: 312540, previous_value: 267880, difference: 44660, growth_rate: 16.67 },
  { metric_name: 'order_count', metric_label: '订单数', current_value: 18732, previous_value: 17240, difference: 1492, growth_rate: 8.65 },
  { metric_name: 'avg_order_value', metric_label: '客单价', current_value: 132.59, previous_value: 126.85, difference: 5.74, growth_rate: 4.52 },
]

const fallbackStores: StoreComparisonItem[] = [
  { store_id: 1, store_name: '朝阳大悦城店', current_revenue: 386540, previous_revenue: 332620, revenue_growth_rate: 16.2, current_profit: 56780, previous_profit: 48620, profit_growth_rate: 16.8, current_order_count: 2860, previous_order_count: 2510, order_growth_rate: 13.9, current_avg_order_value: 135.15, previous_avg_order_value: 132.52, avg_order_value_growth_rate: 2.0 },
  { store_id: 2, store_name: '海淀中关村店', current_revenue: 325210, previous_revenue: 288320, revenue_growth_rate: 12.8, current_profit: 46120, previous_profit: 39870, profit_growth_rate: 15.7, current_order_count: 2420, previous_order_count: 2240, order_growth_rate: 8.0, current_avg_order_value: 134.38, previous_avg_order_value: 128.71, avg_order_value_growth_rate: 4.4 },
  { store_id: 3, store_name: '西城金融街店', current_revenue: 298760, previous_revenue: 270120, revenue_growth_rate: 10.6, current_profit: 38450, previous_profit: 34260, profit_growth_rate: 12.2, current_order_count: 2160, previous_order_count: 2020, order_growth_rate: 6.9, current_avg_order_value: 138.31, previous_avg_order_value: 133.72, avg_order_value_growth_rate: 3.4 },
  { store_id: 4, store_name: '望京凯德店', current_revenue: 245310, previous_revenue: 225260, revenue_growth_rate: 8.9, current_profit: 29670, previous_profit: 27140, profit_growth_rate: 9.3, current_order_count: 1880, previous_order_count: 1760, order_growth_rate: 6.8, current_avg_order_value: 130.48, previous_avg_order_value: 127.99, avg_order_value_growth_rate: 1.9 },
]

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

function hasMetricData(metrics: MetricComparison[]) {
  return metrics.some(item => Math.abs(Number(item.current_value || 0)) + Math.abs(Number(item.previous_value || 0)) > 0)
}

function applyMetricData(metrics: MetricComparison[], currentPeriod: string = DEMO_PERIOD.label, previousPeriod: string = '2024-04') {
  periodInfo.value = { current: currentPeriod, previous: previousPeriod }
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

function fallbackTrendData(metric: string): TrendComparisonResponse {
  const labels = ['05-01', '05-06', '05-11', '05-16', '05-21', '05-26', '05-31']
  const map: Record<string, { label: string; current: number[]; previous: number[] }> = {
    revenue: { label: '营收', current: [76200, 92800, 84500, 108600, 99700, 116200, 124500], previous: [68500, 81300, 79200, 94600, 88300, 102400, 110800] },
    operating_profit: { label: '利润', current: [9800, 11600, 9400, 14700, 12800, 15800, 17600], previous: [8100, 10200, 8700, 12600, 11100, 13700, 14800] },
    order_count: { label: '订单数', current: [560, 690, 640, 820, 760, 880, 930], previous: [520, 620, 590, 740, 700, 805, 846] },
    avg_order_value: { label: '客单价', current: [136, 134, 132, 132, 131, 132, 134], previous: [131, 130, 134, 128, 126, 127, 131] },
  }
  const chosen = map[metric] || map.revenue
  return {
    current_period: DEMO_PERIOD.label,
    previous_period: '2024-04',
    metric_name: metric,
    metric_label: chosen.label,
    data: labels.map((label, index) => ({
      date_label: label,
      current_value: chosen.current[index],
      previous_value: chosen.previous[index],
    })),
  }
}

// ───────────── 数据获取 ─────────────
async function fetchPeriodData() {
  const params = buildQueryParams()
  if (!params) return

  try {
    const res = await getPeriodComparison(params)
    if (res.code === 0 && res.data) {
      const { metrics, current_period, previous_period } = res.data
      applyMetricData(hasMetricData(metrics) ? metrics : fallbackMetrics, current_period, previous_period)
    }
  } catch {
    ElMessage.warning('期间对比接口暂无可用数据，已显示本地样例')
    applyMetricData(fallbackMetrics)
  }
}

async function fetchTrendData() {
  const params = buildQueryParams()
  if (!params) return

  showTrendLoading()
  try {
    const res = await getTrendComparison({ ...params, metric: trendMetric.value })
    if (res.code === 0 && res.data) {
      const hasTrend = res.data.data.some(item => Math.abs(Number(item.current_value || 0)) + Math.abs(Number(item.previous_value || 0)) > 0)
      renderTrendChart(hasTrend ? res.data : fallbackTrendData(trendMetric.value))
    }
  } catch {
    ElMessage.warning('趋势对比接口暂无可用数据，已显示本地样例')
    renderTrendChart(fallbackTrendData(trendMetric.value))
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
      storeData.value = res.data.length ? res.data : fallbackStores
    }
  } catch {
    ElMessage.warning('门店对比接口暂无可用数据，已显示本地样例')
    storeData.value = fallbackStores
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
        itemStyle: { color: COLORS.PRIMARY },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(200, 30, 30, 0.24)' },
              { offset: 1, color: 'rgba(200, 30, 30, 0.03)' }
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
        itemStyle: { color: COLORS.WARNING }
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

  currentDateRange.value = [DEMO_PERIOD.startDate, DEMO_PERIOD.endDate]

  handleQuery()
}

function handleCompareTypeChange() {
  if (filterForm.compare_type !== 'custom') {
    compareDateRange.value = undefined
  }
}

// ───────────── 初始化 ─────────────
onMounted(() => {
  currentDateRange.value = [DEMO_PERIOD.startDate, DEMO_PERIOD.endDate]

  handleQuery()
})
</script>

<style scoped lang="scss">
.comparison-container {
  padding: 0;
  min-height: 100%;
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

.filter-card {
  margin-bottom: 12px;
  border-radius: 6px;
  border: 1px solid #E5DED4;
  background: rgba(255, 253, 249, 0.96);
  box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
  transition: box-shadow var(--transition-duration-base) var(--transition-timing-function-base);

  &:hover {
    box-shadow: var(--shadow-md);
  }

  :deep(.el-card__body) {
    padding: var(--spacing-5);
  }

  :deep(.el-form) {
    margin: 0;
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-4);
    align-items: flex-start;

    .el-form-item {
      margin: 0;
      margin-bottom: var(--spacing-2);

      &.filter-actions {
        flex: 1;
        display: flex;
        justify-content: flex-end;
        gap: var(--spacing-2);
      }
    }
  }

  @media (max-width: var(--breakpoint-md)) {
    :deep(.el-form) {
      .el-form-item {
        width: calc(50% - var(--spacing-4));

        &.filter-actions {
          width: 100%;
          justify-content: flex-start;
        }
      }
    }
  }

  @media (max-width: var(--breakpoint-sm)) {
    :deep(.el-form) {
      .el-form-item {
        width: 100%;

        &.filter-actions {
          width: 100%;
          justify-content: flex-start;
        }
      }
    }
  }
}

.metric-cards {
  margin-bottom: var(--spacing-5);
}

.metric-card {
  text-align: center;
  border-radius: var(--border-radius-md);
  border: var(--border-width-thin) solid var(--color-border-light);
  background-color: var(--color-bg-primary);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-duration-base) var(--transition-timing-function-base);
  height: 100%;
  overflow: hidden;

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    border-color: var(--color-border-primary);
  }

  .metric-label {
    font-size: var(--font-size-sm);
    color: var(--color-text-tertiary);
    margin-bottom: var(--spacing-2);
    text-transform: uppercase;
    letter-spacing: 0;
    font-weight: var(--font-weight-medium);
  }

  .metric-value {
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-primary);
    margin-bottom: var(--spacing-3);
    line-height: 1.2;
  }

  .metric-compare {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: var(--spacing-3);
    font-size: var(--font-size-xs);
    padding-top: var(--spacing-2);
    border-top: var(--border-width-thin) solid var(--color-border-light);

    .previous {
      color: var(--color-text-tertiary);
      font-weight: var(--font-weight-medium);
    }

    .growth {
      font-weight: var(--font-weight-semibold);
      display: inline-flex;
      align-items: center;
      gap: var(--spacing-1);
      padding: var(--spacing-1) var(--spacing-2);
      border-radius: var(--border-radius-sm);
      transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

      .el-icon {
        font-size: var(--font-size-sm);
      }
    }

    .growth-up {
      color: var(--color-success);
      background-color: rgba(var(--color-success-rgb), 0.1);
    }

    .growth-down {
      color: var(--color-danger);
      background-color: rgba(var(--color-danger-rgb), 0.1);
    }

    .growth-flat {
      color: var(--color-text-tertiary);
      background-color: var(--color-bg-secondary);
    }
  }
}

.chart-card,
.table-card {
  margin-bottom: var(--spacing-5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-4) 0;

  .title {
    display: inline-flex;
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

  .period-info {
    font-size: var(--font-size-xs);
    color: var(--color-text-tertiary);
    font-weight: var(--font-weight-medium);
    padding: var(--spacing-1) var(--spacing-2);
    background-color: var(--color-bg-secondary);
    border-radius: var(--border-radius-sm);
    border: var(--border-width-thin) solid var(--color-border-light);
  }
}

.chart-container {
  width: 100%;
  height: calc(var(--spacing-6) * 12.5); // 400px
  border-radius: var(--border-radius-sm);
  overflow: hidden;
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
      letter-spacing: 0;
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
}

// ===== 表单元素样式 =====
.date-range-picker {
  width: calc(var(--spacing-6) * 11.25); // 360px

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
}

:deep(.el-radio-group) {
  .el-radio-button {
    .el-radio-button__inner {
      border-radius: var(--border-radius-sm);
      border: var(--border-width-thin) solid var(--color-border-light);
      background-color: var(--color-bg-primary);
      color: var(--color-text-secondary);
      transition: all var(--transition-duration-fast) var(--transition-timing-function-base);

      &:hover {
        border-color: var(--color-border-base);
        color: var(--color-text-primary);
      }
    }

    &.is-active {
      .el-radio-button__inner {
        background-color: var(--color-primary);
        border-color: var(--color-primary);
        color: var(--color-text-inverse);
        box-shadow: none;

        &:hover {
          background-color: var(--color-primary-dark);
          border-color: var(--color-primary-dark);
        }
      }
    }
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
  .comparison-container {
    padding: var(--spacing-4);
  }

  .metric-cards {
    .el-col {
      margin-bottom: var(--spacing-3);

      &:last-child {
        margin-bottom: 0;
      }
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

  .card-header {
    flex-direction: column;
    gap: var(--spacing-2);
    align-items: flex-start;

    .period-info {
      align-self: flex-end;
      margin-top: var(--spacing-1);
    }
  }
}

@media (max-width: var(--breakpoint-sm)) {
  .comparison-container {
    padding: var(--spacing-3);
  }

  .metric-cards {
    .el-col {
      width: 100%;
      margin-bottom: var(--spacing-2);
    }
  }

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

  .card-header {
    .period-info {
      align-self: stretch;
      text-align: center;
      margin-top: var(--spacing-2);
    }
  }

  .filter-card {
    :deep(.el-form) {
      .el-form-item {
        width: 100%;
      }
    }
  }
}
</style>
