<template>
  <div class="dashboard-container">
    <!-- 顶部操作栏 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" label-width="80px">
        <el-form-item label="门店">
          <StoreSelect v-model="storeId" width="200px" />
        </el-form-item>

        <el-form-item label="时间段">
          <el-radio-group v-model="quickRange" size="small" @change="handleQuickRangeChange">
            <el-radio-button value="today">今日</el-radio-button>
            <el-radio-button value="week">本周</el-radio-button>
            <el-radio-button value="month">本月</el-radio-button>
            <el-radio-button value="custom">自定义</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="quickRange === 'custom'" label="日期">
          <el-date-picker
            v-model="customDateRange"
            type="daterange"
            range-separator="-"
            start-placeholder="开始"
            end-placeholder="结束"
            value-format="YYYY-MM-DD"
            style="width: 300px"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :icon="Search" @click="fetchData">查询</el-button>
          <el-button
            type="success"
            :icon="RefreshRight"
            v-permission="'kpi:rebuild'"
            :loading="rebuildLoading"
            @click="handleRebuildKPI"
          >
            重建KPI
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 核心指标卡片 6 列 -->
    <el-row :gutter="16" class="summary-cards">
      <el-col v-for="(card, idx) in summaryCards" :key="idx" :xs="12" :sm="8" :md="4">
        <el-card shadow="hover" class="summary-card" :class="cardClasses[idx]">
          <div class="card-label">{{ card.label }}</div>
          <div class="card-value">
            <template v-if="card.unit === '元'">¥{{ formatAmount(card.value) }}</template>
            <template v-else-if="card.unit === '%'">{{ card.value.toFixed(2) }}%</template>
            <template v-else>{{ formatInteger(card.value) }}</template>
          </div>
          <div v-if="card.label !== '门店数'" class="card-growth">
            <span class="growth-item">
              <span class="growth-label">同比</span>
              <growth-tag :value="card.yoy_growth" :is-point="card.unit === '%'" />
            </span>
            <span class="growth-item">
              <span class="growth-label">环比</span>
              <growth-tag :value="card.mom_growth" :is-point="card.unit === '%'" />
            </span>
          </div>
          <div v-else class="card-growth">
            <span class="growth-placeholder">活跃门店</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行: 趋势图 + 门店排名 -->
    <el-row :gutter="20">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><TrendCharts /></el-icon>
                营收趋势
              </span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><Histogram /></el-icon>
                门店营收排名 TOP5
              </span>
            </div>
          </template>
          <div ref="storeRankChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 第三行: 费用结构 + 渠道分布 + 利润率仪表盘 -->
    <el-row :gutter="20">
      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><PieChart /></el-icon>
                费用结构
              </span>
            </div>
          </template>
          <div ref="expenseChartRef" class="chart-container-sm"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><PieChart /></el-icon>
                渠道分布
              </span>
            </div>
          </template>
          <div ref="channelChartRef" class="chart-container-sm"></div>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="8">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-header">
              <span class="title">
                <el-icon><Odometer /></el-icon>
                利润率仪表盘
              </span>
            </div>
          </template>
          <div ref="gaugeChartRef" class="chart-container-sm"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h, defineComponent } from 'vue'
import {
  Search,
  RefreshRight,
  TrendCharts,
  Histogram,
  PieChart,
  Odometer
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

import StoreSelect from '@/components/StoreSelect.vue'
import { useECharts, type ECOption } from '@/composables/useECharts'
import { getDashboardOverview } from '@/api/dashboard'
import { rebuildKPI } from '@/api/kpi'
import type {
  SummaryCard,
  TrendDataPoint,
  StoreRankItem,
  ExpenseStructureItem,
  ChannelDistribution
} from '@/types'

// ────────── GrowthTag 内联子组件 ──────────
const GrowthTag = defineComponent({
  name: 'GrowthTag',
  props: {
    value: { type: Number, default: null },
    isPoint: { type: Boolean, default: false }
  },
  setup(props) {
    return () => {
      if (props.value !== null && props.value !== undefined) {
        let color = '#909399'
        if (props.value > 0) color = '#67c23a'
        else if (props.value < 0) color = '#f56c6c'

        let arrow = ''
        if (props.value > 0) arrow = '↑'
        else if (props.value < 0) arrow = '↓'

        const suffix = props.isPoint ? '点' : '%'
        return h('span', { style: { color, fontWeight: 'bold' } }, `${arrow}${Math.abs(props.value)}${suffix}`)
      }
      return h('span', { style: { color: '#c0c4cc' } }, '--')
    }
  }
})

// ────────── 筛选状态 ──────────
const storeId = ref<number | undefined>(undefined)
const quickRange = ref<'today' | 'week' | 'month' | 'custom'>('month')
const customDateRange = ref<[string, string]>()
const rebuildLoading = ref(false)

// ────────── 卡片数据 ──────────
const summaryCards = ref<SummaryCard[]>([])
const cardClasses = ['card-revenue', 'card-profit', 'card-order', 'card-aov', 'card-rate', 'card-store']

// ────────── 图表 refs ──────────
const trendChartRef = ref<HTMLElement | null>(null)
const storeRankChartRef = ref<HTMLElement | null>(null)
const expenseChartRef = ref<HTMLElement | null>(null)
const channelChartRef = ref<HTMLElement | null>(null)
const gaugeChartRef = ref<HTMLElement | null>(null)

const { setOption: setTrendOption, showLoading: showTrendLoading, hideLoading: hideTrendLoading } = useECharts(trendChartRef)
const { setOption: setRankOption } = useECharts(storeRankChartRef)
const { setOption: setExpenseOption } = useECharts(expenseChartRef)
const { setOption: setChannelOption } = useECharts(channelChartRef)
const { setOption: setGaugeOption } = useECharts(gaugeChartRef)

// ────────── 工具函数 ──────────
function formatAmount(val: number): string {
  if (val >= 10000) return (val / 10000).toFixed(2) + '万'
  return val.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatInteger(val: number): string {
  return Math.round(val).toLocaleString('zh-CN')
}

function getDateRange(): { start_date: string; end_date: string } {
  const today = dayjs()
  switch (quickRange.value) {
    case 'today':
      return { start_date: today.format('YYYY-MM-DD'), end_date: today.format('YYYY-MM-DD') }
    case 'week': {
      const monday = today.startOf('week').add(1, 'day') // dayjs week starts Sunday
      return { start_date: monday.format('YYYY-MM-DD'), end_date: today.format('YYYY-MM-DD') }
    }
    case 'month':
      return { start_date: today.startOf('month').format('YYYY-MM-DD'), end_date: today.format('YYYY-MM-DD') }
    case 'custom':
      if (customDateRange.value && customDateRange.value.length === 2) {
        return { start_date: customDateRange.value[0], end_date: customDateRange.value[1] }
      }
      return { start_date: today.startOf('month').format('YYYY-MM-DD'), end_date: today.format('YYYY-MM-DD') }
  }
}

function handleQuickRangeChange() {
  if (quickRange.value !== 'custom') {
    fetchData()
  }
}

// ────────── 数据获取 ──────────
async function fetchData() {
  const range = getDateRange()
  showTrendLoading()

  try {
    const res = await getDashboardOverview({
      ...range,
      store_id: storeId.value
    })

    if ((res.code === 0 || res.code === 200) && res.data) {
      const data = res.data
      summaryCards.value = data.summary_cards
      renderTrendChart(data.revenue_trend)
      renderStoreRankChart(data.store_ranking)
      renderExpenseChart(data.expense_structure)
      renderChannelChart(data.channel_distribution)
      renderGaugeChart(data.profit_rate, data.profit_rate_target)
    }
  } catch {
    ElMessage.error('加载仪表盘数据失败')
  } finally {
    hideTrendLoading()
  }
}

// ────────── 趋势折线图 ──────────
function renderTrendChart(data: TrendDataPoint[]) {
  if (!data || data.length === 0) {
    setTrendOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } } })
    return
  }

  const dates = data.map(d => d.date)
  const revenues = data.map(d => d.revenue)
  const costs = data.map(d => d.cost)
  const profits = data.map(d => d.profit)

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' },
      formatter: (params: any) => {
        let html = `<div style="font-weight:bold;margin-bottom:5px">${params[0].axisValue}</div>`
        params.forEach((p: any) => {
          html += `<div style="display:flex;justify-content:space-between;gap:20px"><span>${p.marker}${p.seriesName}</span><b>¥${p.value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</b></div>`
        })
        return html
      }
    },
    legend: { data: ['营收', '成本', '利润'], top: 10 },
    grid: { left: '3%', right: '4%', bottom: dates.length > 30 ? '18%' : '3%', top: 60, containLabel: true },
    dataZoom: dates.length > 30 ? [{ type: 'slider', bottom: 5, height: 20 }] : [],
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates,
      axisLabel: { rotate: dates.length > 15 ? 45 : 0 }
    },
    yAxis: {
      type: 'value',
      name: '金额(元)',
      axisLabel: {
        formatter: (v: number) => v >= 10000 ? (v / 10000).toFixed(1) + 'w' : String(v)
      }
    },
    series: [
      {
        name: '营收', type: 'line', data: revenues, smooth: true,
        itemStyle: { color: '#67c23a' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(103,194,58,0.3)' }, { offset: 1, color: 'rgba(103,194,58,0.05)' }] } }
      },
      {
        name: '成本', type: 'line', data: costs, smooth: true,
        itemStyle: { color: '#e6a23c' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(230,162,60,0.3)' }, { offset: 1, color: 'rgba(230,162,60,0.05)' }] } }
      },
      {
        name: '利润', type: 'line', data: profits, smooth: true,
        itemStyle: { color: '#409eff' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(64,158,255,0.3)' }, { offset: 1, color: 'rgba(64,158,255,0.05)' }] } }
      }
    ]
  }
  setTrendOption(option, true)
}

// ────────── 门店排名(横向条形图) ──────────
function renderStoreRankChart(data: StoreRankItem[]) {
  if (!data || data.length === 0) {
    setRankOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } } })
    return
  }

  // 倒序让第1名显示在最上面
  const reversed = [...data].reverse()
  const names = reversed.map(d => d.store_name)
  const values = reversed.map(d => d.revenue)

  const colors = ['#cce5ff', '#99caff', '#66b0ff', '#3395ff', '#007bff']
  const barColors = reversed.map((_, i) => colors[Math.min(i, colors.length - 1)])

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: any) => {
        const p = params[0]
        const item = reversed[p.dataIndex]
        return `<b>${item.store_name}</b><br/>营收: ¥${item.revenue.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}<br/>利润: ¥${item.profit.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}`
      }
    },
    grid: { left: '3%', right: '15%', bottom: '3%', top: '3%', containLabel: true },
    xAxis: { type: 'value', show: false },
    yAxis: {
      type: 'category',
      data: names,
      axisLine: { show: false },
      axisTick: { show: false }
    },
    series: [{
      type: 'bar',
      data: values.map((v, i) => ({
        value: v,
        itemStyle: {
          color: barColors[i],
          borderRadius: [0, 4, 4, 0]
        }
      })),
      barWidth: 16,
      label: {
        show: true,
        position: 'right',
        formatter: (p: any) => '¥' + p.value.toLocaleString('zh-CN', { minimumFractionDigits: 0 }),
        fontSize: 11,
        color: '#606266'
      }
    }]
  }
  setRankOption(option, true)
}

// ────────── 费用结构(环形图) ──────────
function renderExpenseChart(data: ExpenseStructureItem[]) {
  if (!data || data.length === 0) {
    setExpenseOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } } })
    return
  }

  const total = data.reduce((s, d) => s + d.value, 0)

  const option: ECOption = {
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => `${p.name}<br/>¥${p.value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}<br/>占比 ${p.percent}%`
    },
    legend: { bottom: 0, type: 'scroll' },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '45%'],
      data: data.map(d => ({ name: d.name, value: d.value })),
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.2)' } },
      label: { show: false },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 2
      }
    }],
    graphic: [{
      type: 'text',
      left: 'center',
      top: '40%',
      style: {
        text: '¥' + formatAmount(total),
        fontSize: 16,
        fontWeight: 'bold',
        fill: '#303133',
        textAlign: 'center'
      }
    }, {
      type: 'text',
      left: 'center',
      top: '48%',
      style: {
        text: '总费用',
        fontSize: 12,
        fill: '#909399',
        textAlign: 'center'
      }
    }]
  }
  setExpenseOption(option, true)
}

// ────────── 渠道分布(环形图) ──────────
function renderChannelChart(data: ChannelDistribution) {
  const items = [
    { name: '堂食', value: data.dine_in },
    { name: '外带', value: data.takeout },
    { name: '外卖', value: data.delivery },
    { name: '线上', value: data.online }
  ]
  const total = items.reduce((s, d) => s + d.value, 0)

  if (total === 0) {
    setChannelOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: '#999', fontSize: 14 } } })
    return
  }

  const option: ECOption = {
    tooltip: {
      trigger: 'item',
      formatter: (p: any) => `${p.name}<br/>¥${p.value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}<br/>占比 ${p.percent}%`
    },
    legend: { bottom: 0, type: 'scroll' },
    series: [{
      type: 'pie',
      radius: ['45%', '70%'],
      center: ['50%', '45%'],
      data: items,
      emphasis: { itemStyle: { shadowBlur: 10, shadowOffsetX: 0, shadowColor: 'rgba(0,0,0,0.2)' } },
      label: { show: false },
      itemStyle: {
        borderColor: '#fff',
        borderWidth: 2
      },
      color: ['#409eff', '#67c23a', '#e6a23c', '#f56c6c']
    }],
    graphic: [{
      type: 'text',
      left: 'center',
      top: '40%',
      style: {
        text: '¥' + formatAmount(total),
        fontSize: 16,
        fontWeight: 'bold',
        fill: '#303133',
        textAlign: 'center'
      }
    }, {
      type: 'text',
      left: 'center',
      top: '48%',
      style: {
        text: '总收入',
        fontSize: 12,
        fill: '#909399',
        textAlign: 'center'
      }
    }]
  }
  setChannelOption(option, true)
}

// ────────── 利润率仪表盘(Gauge) ──────────
function renderGaugeChart(profitRate: number, target: number) {
  const option: ECOption = {
    series: [{
      type: 'gauge',
      min: 0,
      max: 40,
      splitNumber: 8,
      radius: '85%',
      axisLine: {
        lineStyle: {
          width: 20,
          color: [
            [0.2, '#f56c6c'],   // 0-8%  红
            [0.375, '#e6a23c'],  // 8-15% 黄
            [1, '#67c23a']       // 15-40% 绿
          ]
        }
      },
      pointer: {
        width: 5,
        length: '60%',
        itemStyle: { color: 'auto' }
      },
      axisTick: { distance: -20, length: 6, lineStyle: { color: '#fff', width: 1 } },
      splitLine: { distance: -20, length: 20, lineStyle: { color: '#fff', width: 2 } },
      axisLabel: {
        distance: 25,
        fontSize: 11,
        formatter: (v: number) => v + '%'
      },
      detail: {
        valueAnimation: true,
        formatter: (v: number) => v.toFixed(2) + '%',
        fontSize: 22,
        fontWeight: 'bold',
        offsetCenter: [0, '70%'],
        color: 'inherit'
      },
      title: {
        offsetCenter: [0, '90%'],
        fontSize: 13,
        color: '#909399'
      },
      data: [{ value: profitRate, name: '当前利润率' }],
      // 目标线 markLine
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', color: '#909399' },
        label: { formatter: `目标 ${target}%`, fontSize: 10 }
      }
    }]
  }
  setGaugeOption(option, true)
}

// ────────── KPI 重建 ──────────
async function handleRebuildKPI() {
  try {
    await ElMessageBox.confirm(
      '重建 KPI 会重新计算所选日期范围内的所有 KPI 数据，是否继续？',
      '确认重建',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    rebuildLoading.value = true
    const range = getDateRange()
    const { data } = await rebuildKPI(range)
    ElMessage.success(`重建成功！影响 ${data.total_records} 条记录（${data.affected_stores} 个门店，${data.affected_dates} 天）`)
    await fetchData()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('重建 KPI 失败:', error)
    }
  } finally {
    rebuildLoading.value = false
  }
}

// ────────── 初始化 ──────────
onMounted(() => {
  fetchData()
})
</script>

<style scoped lang="scss">
.dashboard-container {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
  :deep(.el-card__body) { padding: 20px; }
  .el-form { margin: 0; }
}

/* ───── 核心指标卡片 ───── */
.summary-cards {
  margin-bottom: 20px;
}

.summary-card {
  text-align: center;
  transition: transform 0.3s, box-shadow 0.3s;
  margin-bottom: 16px;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }

  :deep(.el-card__body) {
    padding: 20px 12px;
  }

  .card-label {
    font-size: 13px;
    color: #909399;
    margin-bottom: 8px;
  }

  .card-value {
    font-size: 28px;
    font-weight: bold;
    color: #303133;
    margin-bottom: 10px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .card-growth {
    display: flex;
    justify-content: center;
    gap: 16px;
    font-size: 12px;

    .growth-item {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .growth-label {
      color: #c0c4cc;
    }

    .growth-placeholder {
      color: #c0c4cc;
    }
  }

  &.card-revenue .card-value { color: #67c23a; }
  &.card-profit .card-value { color: #409eff; }
  &.card-order .card-value { color: #e6a23c; }
  &.card-aov .card-value { color: #909399; }
  &.card-rate .card-value { color: #f56c6c; }
  &.card-store .card-value { color: #9b59b6; }
}

/* ───── 图表卡片 ───── */
.chart-card {
  margin-bottom: 20px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .title {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 16px;
      font-weight: 600;
    }
  }
}

.chart-container {
  width: 100%;
  height: 400px;
}

.chart-container-sm {
  width: 100%;
  height: 340px;
}
</style>
