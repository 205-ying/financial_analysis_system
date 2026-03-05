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
import { COLORS } from '@/utils/colors'
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
          :style="{ color: value > 0 ? 'var(--color-success)' : value < 0 ? 'var(--color-danger)' : 'var(--color-text-tertiary)', fontWeight: 'bold' }">
      {{ value > 0 ? '↑' : value < 0 ? '↓' : '' }}{{ Math.abs(value) }}%
    </span>
    <span v-else style="color: var(--color-text-tertiary)">--</span>
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
        itemStyle: { color: COLORS.PRIMARY },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(30, 58, 138, 0.3)' }, // #1E3A8A with opacity
              { offset: 1, color: 'rgba(30, 58, 138, 0.05)' }
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
  padding: var(--spacing-5) var(--spacing-5) var(--spacing-6);
  background-color: var(--color-bg-secondary);
  min-height: calc(100vh - var(--spacing-8)); // 减去顶部导航高度
}

.filter-card {
  margin-bottom: var(--spacing-5);
  border-radius: var(--border-radius-md);
  border: var(--border-width-thin) solid var(--color-border-light);
  background-color: var(--color-bg-primary);
  box-shadow: var(--shadow-sm);
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

      &:last-child {
        flex: 1;
        display: flex;
        justify-content: flex-end;
        gap: var(--spacing-2);
        margin-top: var(--spacing-2);
      }
    }
  }

  @media (max-width: var(--breakpoint-md)) {
    :deep(.el-form) {
      .el-form-item {
        width: calc(50% - var(--spacing-4));

        &:last-child {
          width: 100%;
          justify-content: center;
        }
      }
    }
  }

  @media (max-width: var(--breakpoint-sm)) {
    :deep(.el-form) {
      .el-form-item {
        width: 100%;

        &:last-child {
          width: 100%;
          justify-content: center;
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
    letter-spacing: 0.5px;
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
