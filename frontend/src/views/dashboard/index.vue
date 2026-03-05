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
            <el-radio-button value="last_month">上月</el-radio-button>
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
            v-permission="PERMISSIONS.KPI_REBUILD"
            type="success"
            :icon="RefreshRight"
            :loading="rebuildLoading"
            @click="handleRebuildKPI"
          >
            重建KPI
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 核心指标便当盒 Bento Grid -->
    <div class="bento-grid">
      <div v-for="(card, idx) in summaryCards" :key="idx" class="bento-item" :class="cardClasses[idx]">
        <div class="bento-content">
          <div class="card-label">{{ card.label }}</div>
          <div class="card-value font-number">
            <template v-if="card.unit === '元'"><span class="unit">¥</span>{{ formatAmount(card.value) }}</template>
            <template v-else-if="card.unit === '%'">{{ card.value.toFixed(2) }}<span class="unit">%</span></template>
            <template v-else>{{ formatInteger(card.value) }}</template>
          </div>
          <div v-if="card.label !== '门店数'" class="card-growth">
            <span class="growth-item">
              <span class="growth-label">同比</span>
              <growth-tag :value="card.yoy_growth ?? undefined" :is-point="card.unit === '%'" />
            </span>
            <span class="growth-item">
              <span class="growth-label">环比</span>
              <growth-tag :value="card.mom_growth ?? undefined" :is-point="card.unit === '%'" />
            </span>
          </div>
          <div v-else class="card-growth">
            <span class="growth-placeholder">活跃门店</span>
          </div>
        </div>
        
        <!-- 微型趋势图 Sparklines -->
        <div v-if="['营业收入', '利润', '净利润', '订单总数', '客单价'].includes(card.label)" class="sparkline-box">
          <svg viewBox="0 0 100 30" preserveAspectRatio="none" class="sparkline-svg">
            <defs>
              <linearGradient :id="`spark-grad-${idx}`" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" :stop-color="(card.mom_growth ?? 0) >= 0 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'" />
                <stop offset="100%" :stop-color="(card.mom_growth ?? 0) >= 0 ? 'rgba(16, 185, 129, 0)' : 'rgba(239, 68, 68, 0)'" />
              </linearGradient>
            </defs>
            <path :d="(card.mom_growth ?? 0) >= 0 ? 'M 0 25 C 20 15, 40 25, 60 10 S 80 15, 100 2 L 100 30 L 0 30 Z' : 'M 0 5 C 20 10, 40 5, 60 20 S 80 15, 100 28 L 100 30 L 0 30 Z'" :fill="`url(#spark-grad-${idx})`" />
            <path :d="(card.mom_growth ?? 0) >= 0 ? 'M 0 25 C 20 15, 40 25, 60 10 S 80 15, 100 2' : 'M 0 5 C 20 10, 40 5, 60 20 S 80 15, 100 28'" fill="none" :stroke="(card.mom_growth ?? 0) >= 0 ? '#10B981' : '#EF4444'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </div>
      </div>
    </div>

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
import { ref, onMounted, h, defineComponent, nextTick } from 'vue'
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
import { COLORS, CHART_PALETTE } from '@/utils/colors'

import StoreSelect from '@/components/StoreSelect.vue'
import { useECharts, type ECOption } from '@/composables/useECharts'
import { getDashboardOverview } from '@/api/dashboard'
import { rebuildKPI } from '@/api/kpi'
import { PERMISSIONS } from '@/config'
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
        let color: string = COLORS.GRAY_500
        if (props.value > 0) color = COLORS.SUCCESS
        else if (props.value < 0) color = COLORS.DANGER

        let arrow = ''
        if (props.value > 0) arrow = '↑'
        else if (props.value < 0) arrow = '↓'

        const suffix = props.isPoint ? '点' : '%'
        return h('span', { style: { color, fontWeight: 'bold' } }, `${arrow}${Math.abs(props.value)}${suffix}`)
      }
      return h('span', { style: { color: COLORS.GRAY_300 } }, '--')
    }
  }
})

// ────────── 筛选状态 ──────────
const storeId = ref<number | undefined>(undefined)
const quickRange = ref<'today' | 'week' | 'last_month' | 'month' | 'custom'>('last_month')
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
    case 'last_month': {
      const lastMonth = today.subtract(1, 'month')
      return { start_date: lastMonth.startOf('month').format('YYYY-MM-DD'), end_date: lastMonth.endOf('month').format('YYYY-MM-DD') }
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
      summaryCards.value = data.summary_cards || []
      renderTrendChart(data.revenue_trend || [])
      renderStoreRankChart(data.store_ranking || [])
      renderExpenseChart(data.expense_structure || [])
      renderChannelChart(data.channel_distribution || { dine_in: 0, takeout: 0, delivery: 0, online: 0 })
      renderGaugeChart(data.profit_rate || 0, data.profit_rate_target || 0)
    } else {
      // 数据异常时显示空状态
      summaryCards.value = []
      renderTrendChart([])
      renderStoreRankChart([])
      renderExpenseChart([])
      renderChannelChart({ dine_in: 0, takeout: 0, delivery: 0, online: 0 })
      renderGaugeChart(0, 0)
    }
  } catch {
    ElMessage.error('加载仪表盘数据失败')
    // 出错时也显示空状态
    summaryCards.value = []
    renderTrendChart([])
    renderStoreRankChart([])
    renderExpenseChart([])
    renderChannelChart({ dine_in: 0, takeout: 0, delivery: 0, online: 0 })
    renderGaugeChart(0, 0)
  } finally {
    hideTrendLoading()
  }
}

// ────────── 趋势折线图 ──────────
function renderTrendChart(data: TrendDataPoint[]) {
  if (!data || data.length === 0) {
    setTrendOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: COLORS.GRAY_400, fontSize: 14 } } })
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
      formatter: (params: unknown) => {
        const list = Array.isArray(params) ? params : []
        const axisValue = (list[0] as { axisValue?: unknown } | undefined)?.axisValue
        const title = typeof axisValue === 'string' ? axisValue : ''
        let html = `<div style="font-weight:bold;margin-bottom:5px">${title}</div>`
        list.forEach((raw) => {
          const p = raw as { marker?: unknown; seriesName?: unknown; value?: unknown }
          const marker = typeof p.marker === 'string' ? p.marker : ''
          const seriesName = typeof p.seriesName === 'string' ? p.seriesName : ''
          const value = typeof p.value === 'number' ? p.value : 0
          html += `<div style="display:flex;justify-content:space-between;gap:20px"><span>${marker}${seriesName}</span><b>¥${value.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}</b></div>`
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
        itemStyle: { color: CHART_PALETTE.FINANCIAL.REVENUE },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(16, 185, 129, 0.3)' }, { offset: 1, color: 'rgba(16, 185, 129, 0.05)' }] } }
      },
      {
        name: '成本', type: 'line', data: costs, smooth: true,
        itemStyle: { color: CHART_PALETTE.FINANCIAL.COST },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(245, 158, 11, 0.3)' }, { offset: 1, color: 'rgba(245, 158, 11, 0.05)' }] } }
      },
      {
        name: '利润', type: 'line', data: profits, smooth: true,
        itemStyle: { color: CHART_PALETTE.FINANCIAL.PROFIT },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(30, 58, 138, 0.3)' }, { offset: 1, color: 'rgba(30, 58, 138, 0.05)' }] } }
      }
    ]
  }
  setTrendOption(option, true)
}

// ────────── 门店排名(横向条形图) ──────────
function renderStoreRankChart(data: StoreRankItem[]) {
  if (!data || data.length === 0) {
    setRankOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: COLORS.GRAY_400, fontSize: 14 } } })
    return
  }

  // 倒序让第1名显示在最上面
  const reversed = [...data].reverse()
  const names = reversed.map(d => d.store_name)
  const values = reversed.map(d => d.revenue)

  // 使用主色调的渐变
  const colors = [
    'rgba(30, 58, 138, 0.1)',
    'rgba(30, 58, 138, 0.2)',
    'rgba(30, 58, 138, 0.3)',
    'rgba(30, 58, 138, 0.4)',
    'rgba(30, 58, 138, 0.5)'
  ]
  const barColors = reversed.map((_, i) => colors[Math.min(i, colors.length - 1)])

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => {
        const first = Array.isArray(params) ? params[0] : undefined
        const dataIndex = (first as { dataIndex?: unknown } | undefined)?.dataIndex
        if (typeof dataIndex !== 'number') return ''
        const item = reversed[dataIndex]
        if (!item) return ''
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
        formatter: (p: unknown) => {
          const value = (p as { value?: unknown } | undefined)?.value
          const num = typeof value === 'number' ? value : Number(value)
          const safe = Number.isFinite(num) ? num : 0
          return '¥' + safe.toLocaleString('zh-CN', { minimumFractionDigits: 0 })
        },
        fontSize: 11,
        color: COLORS.GRAY_600
      }
    }]
  }
  setRankOption(option, true)
}

// ────────── 费用结构(环形图) ──────────
function renderExpenseChart(data: ExpenseStructureItem[]) {
  if (!data || data.length === 0) {
    setExpenseOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: COLORS.GRAY_400, fontSize: 14 } } })
    return
  }

  const total = data.reduce((s, d) => s + d.value, 0)

  const option: ECOption = {
    tooltip: {
      trigger: 'item',
      formatter: (p: unknown) => {
        const pp = p as { name?: unknown; value?: unknown; percent?: unknown }
        const name = typeof pp.name === 'string' ? pp.name : ''
        const value = typeof pp.value === 'number' ? pp.value : Number(pp.value)
        const safeValue = Number.isFinite(value) ? value : 0
        const percent = typeof pp.percent === 'number' ? pp.percent : Number(pp.percent)
        const safePercent = Number.isFinite(percent) ? percent : 0
        return `${name}<br/>¥${safeValue.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}<br/>占比 ${safePercent}%`
      }
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
        borderColor: COLORS.WHITE,
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
        fill: COLORS.GRAY_900
      }
    }, {
      type: 'text',
      left: 'center',
      top: '48%',
      style: {
        text: '总费用',
        fontSize: 12,
        fill: COLORS.GRAY_500
      }
    }]
  }
  setExpenseOption(option, true)
}

// ────────── 渠道分布(环形图) ──────────
function renderChannelChart(data: ChannelDistribution) {
  // 检查容器是否存在
  if (!channelChartRef.value) {
    return
  }
  
  const items = [
    { name: '堂食', value: data.dine_in },
    { name: '外带', value: data.takeout },
    { name: '外卖', value: data.delivery },
    { name: '线上', value: data.online }
  ]
  const total = items.reduce((s, d) => s + d.value, 0)

  if (total === 0) {
    setChannelOption({ title: { text: '暂无数据', left: 'center', top: 'center', textStyle: { color: COLORS.GRAY_400, fontSize: 14 } } })
    return
  }

  const option: ECOption = {
    tooltip: {
      trigger: 'item',
      formatter: (p: unknown) => {
        const pp = p as { name?: unknown; value?: unknown; percent?: unknown }
        const name = typeof pp.name === 'string' ? pp.name : ''
        const value = typeof pp.value === 'number' ? pp.value : Number(pp.value)
        const safeValue = Number.isFinite(value) ? value : 0
        const percent = typeof pp.percent === 'number' ? pp.percent : Number(pp.percent)
        const safePercent = Number.isFinite(percent) ? percent : 0
        return `${name}<br/>¥${safeValue.toLocaleString('zh-CN', { minimumFractionDigits: 2 })}<br/>占比 ${safePercent}%`
      }
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
        borderColor: COLORS.WHITE,
        borderWidth: 2
      },
      color: [
        CHART_PALETTE.CATEGORY[0],  // 主色
        CHART_PALETTE.CATEGORY[2],  // 成功色
        CHART_PALETTE.CATEGORY[3],  // 警告色
        CHART_PALETTE.CATEGORY[4]   // 危险色
      ]
    }],
    graphic: [{
      type: 'text',
      left: 'center',
      top: '40%',
      style: {
        text: '¥' + formatAmount(total),
        fontSize: 16,
        fontWeight: 'bold',
        fill: COLORS.GRAY_900
      }
    }, {
      type: 'text',
      left: 'center',
      top: '48%',
      style: {
        text: '总收入',
        fontSize: 12,
        fill: COLORS.GRAY_500
      }
    }]
  }
  setChannelOption(option, true)
}

// ────────── 利润率仪表盘(Gauge) ──────────
function renderGaugeChart(profitRate: number, target: number) {
  // 检查容器是否存在
  if (!gaugeChartRef.value) {
    return
  }
  
  const safeProfitRate = Number.isFinite(profitRate) ? profitRate : 0
  const safeTarget = Number.isFinite(target) && target > 0 ? target : 15
  
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
            [0.2, COLORS.DANGER],      // 0-8%  红
            [0.375, COLORS.WARNING],   // 8-15% 黄
            [1, COLORS.SUCCESS]        // 15-40% 绿
          ]
        }
      },
      pointer: {
        width: 5,
        length: '60%',
        itemStyle: { color: 'auto' }
      },
      axisTick: { distance: -20, length: 6, lineStyle: { color: COLORS.WHITE, width: 1 } },
      splitLine: { distance: -20, length: 20, lineStyle: { color: COLORS.WHITE, width: 2 } },
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
        color: COLORS.GRAY_500
      },
      data: [{ value: safeProfitRate, name: '当前利润率' }],
      // 目标线 markLine
      markLine: {
        silent: true,
        symbol: 'none',
        lineStyle: { type: 'dashed', color: COLORS.GRAY_500 },
        label: { formatter: `目标 ${safeTarget}%`, fontSize: 10 }
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
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error('重建 KPI 失败')
    }
  } finally {
    rebuildLoading.value = false
  }
}

// ────────── 初始化 ──────────
onMounted(async () => {
  // 等待DOM完全渲染，确保图表容器已挂载
  await nextTick()
  // 延迟一小段时间确保图表实例初始化完成
  setTimeout(() => {
    fetchData()
  }, 100)
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

/* ───── 核心指标便当盒 Bento Grid ───── */
.bento-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  background-color: #ffffff;
  border-radius: 12px;
  border: 1px solid #E2E8F0;
  box-shadow: 0 4px 20px -2px rgba(67, 56, 202, 0.05);
  margin-bottom: 24px;
  overflow: hidden;

  /* 物理细线切割 */
  .bento-item {
    border-right: 1px solid #E2E8F0;
  }
  .bento-item:last-child {
    border-right: none;
  }

  @media (max-width: 1400px) {
    grid-template-columns: repeat(3, 1fr);
    
    .bento-item {
      border-right: 1px solid #E2E8F0;
      border-bottom: 1px solid #E2E8F0;
    }
    .bento-item:nth-child(3n) {
      border-right: none;
    }
    /* 最后一行无底边框 */
    .bento-item:nth-last-child(-n+3) {
      border-bottom: none;
    }
    /* 修正最后一个的右边框（如果是3的倍数，上面已经去除了） */
  }

  @media (max-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
    
    .bento-item {
      border-right: 1px solid #E2E8F0;
      border-bottom: 1px solid #E2E8F0;
    }
    .bento-item:nth-child(even) {
      border-right: none;
    }
    /* 恢复被覆盖的基础媒体查询样式 */
    .bento-item:nth-child(3n) {
      border-right: 1px solid #E2E8F0; /* reset from 1400px */
    }
    .bento-item:nth-child(even) {
      border-right: none !important; 
    }
    .bento-item:nth-last-child(-n+3) {
      border-bottom: 1px solid #E2E8F0; /* reset from 1400px */
    }
    .bento-item:nth-last-child(-n+2) {
      border-bottom: none !important;
    }
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    
    .bento-item {
      border-right: none !important;
      border-bottom: 1px solid #E2E8F0 !important;
    }
    .bento-item:last-child {
      border-bottom: none !important;
    }
  }
}

.bento-item {
  padding: 24px;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  overflow: hidden;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #F8FAFC;
    .sparkline-svg {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .bento-content {
    position: relative;
    z-index: 2;
  }

  .card-label {
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-secondary, #64748B);
    margin-bottom: 12px;
  }

  .card-value {
    font-size: 36px;
    font-weight: 800;
    color: #0F172A; /* 深灰 */
    font-family: 'Inter', 'Roboto', 'DIN', sans-serif;
    margin-bottom: 16px;
    line-height: 1.2;
    letter-spacing: -0.5px;
    
    .unit {
      font-size: 16px;
      font-weight: 600;
      color: #64748B;
      margin: 0 4px;
    }
  }

  .card-growth {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px; /* 缩小辅助文字 */

    .growth-item {
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    .growth-label {
      color: #64748B; /* 置灰色阶 */
      font-weight: 500;
    }

    .growth-placeholder {
      color: transparent;
    }
  }

  /* 微型趋势图 Sparklines 样式 */
  .sparkline-box {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 60px;
    z-index: 1;
    pointer-events: none;
  }

  .sparkline-svg {
    width: 100%;
    height: 100%;
    opacity: 0.6;
    transform: translateY(6px);
    transition: all 0.4s ease;
  }
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
