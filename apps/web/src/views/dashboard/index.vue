<template>
  <div class="dashboard-page">
    <section class="dashboard-toolbar">
      <div>
        <p class="eyebrow">财务驾驶舱</p>
        <h1>今日经营</h1>
      </div>

      <div class="toolbar-controls">
        <StoreSelect v-model="storeId" width="156px" />
        <el-radio-group v-model="quickRange" size="small" @change="handleQuickRangeChange">
          <el-radio-button value="demo">演示月</el-radio-button>
          <el-radio-button value="today">今日</el-radio-button>
          <el-radio-button value="week">本周</el-radio-button>
          <el-radio-button value="last_month">上月</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
          <el-radio-button value="custom">自定义</el-radio-button>
        </el-radio-group>
        <el-date-picker
          v-if="quickRange === 'custom'"
          v-model="customDateRange"
          type="daterange"
          range-separator="~"
          start-placeholder="开始"
          end-placeholder="结束"
          value-format="YYYY-MM-DD"
          class="custom-date"
        />
        <el-button type="primary" :icon="Search" @click="fetchData">查询</el-button>
        <el-button
          v-permission="PERMISSIONS.KPI_REBUILD"
          class="ghost-action"
          :icon="RefreshRight"
          :loading="rebuildLoading"
          @click="handleRebuildKPI"
        >
          重建KPI
        </el-button>
      </div>
    </section>

    <div class="data-freshness">数据更新：{{ updatedAt }}</div>

    <section class="metric-grid">
      <article v-for="card in dashboardCards" :key="card.key" class="metric-card">
        <div class="metric-head">
          <span>{{ card.label }}</span>
          <el-icon :class="card.tone"><component :is="card.icon" /></el-icon>
        </div>
        <div class="metric-value font-number">{{ card.display }}</div>
        <div class="metric-trends">
          <span>较上月 <b :class="trendClass(card.mom)">{{ formatTrend(card.mom, card.isPoint) }}</b></span>
          <span>较去年同期 <b :class="trendClass(card.yoy)">{{ formatTrend(card.yoy, card.isPoint) }}</b></span>
        </div>
        <div class="spark-bars">
          <i
            v-for="(height, index) in card.spark"
            :key="index"
            :style="{ height: `${height}%` }"
          />
        </div>
      </article>
    </section>

    <section class="dashboard-grid">
      <article class="panel panel-wide">
        <header class="panel-header">
          <div>
            <h2>利润瀑布图</h2>
            <span>本期累计</span>
          </div>
          <div class="panel-actions">
            <el-radio-group v-model="waterfallMode" size="small" class="mode-switch">
              <el-radio-button value="图形">图形</el-radio-button>
              <el-radio-button value="表格">表格</el-radio-button>
            </el-radio-group>
            <small>单位：元</small>
          </div>
        </header>
        <div ref="waterfallChartRef" class="waterfall-chart"></div>
      </article>

      <article class="panel risk-panel">
        <header class="panel-header">
          <div>
            <h2>经营风险预警</h2>
            <span>按影响优先级排序</span>
          </div>
          <button type="button" class="text-link">更多</button>
        </header>

        <div class="risk-table">
          <div class="risk-row risk-head">
            <span>预警类型</span>
            <span>预警内容</span>
            <span>影响</span>
            <span>时间</span>
          </div>
          <div v-for="item in riskAlerts" :key="item.title" class="risk-row">
            <span class="risk-type">
              <i :class="item.tone"><el-icon><component :is="item.icon" /></el-icon></i>
              {{ item.title }}
            </span>
            <span>{{ item.content }}</span>
            <span><b :class="['risk-badge', item.levelClass]">{{ item.level }}</b></span>
            <span>{{ item.time }}</span>
          </div>
        </div>
      </article>
    </section>

    <section class="lower-grid">
      <article class="panel">
        <header class="panel-header compact">
          <div>
            <h2>门店经营对比</h2>
            <span>本期累计</span>
          </div>
          <button type="button" class="text-link">更多</button>
        </header>
        <table class="finance-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>门店</th>
              <th>营业收入</th>
              <th>净利润</th>
              <th>利润率</th>
              <th>较上月</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in storeRows" :key="row.store_name">
              <td><span class="rank-dot">{{ index + 1 }}</span></td>
              <td>{{ row.store_name }}</td>
              <td>{{ compactCurrency(row.revenue) }}</td>
              <td>{{ compactCurrency(row.profit) }}</td>
              <td>{{ ratio(row.profit, row.revenue) }}</td>
              <td class="positive">↑ {{ (16.2 - index * 1.3).toFixed(1) }}%</td>
            </tr>
          </tbody>
          <tfoot>
            <tr>
              <td colspan="2">合计</td>
              <td>{{ compactCurrency(storeTotal.revenue) }}</td>
              <td>{{ compactCurrency(storeTotal.profit) }}</td>
              <td>{{ ratio(storeTotal.profit, storeTotal.revenue) }}</td>
              <td class="positive">↑ 10.6%</td>
            </tr>
          </tfoot>
        </table>
      </article>

      <article class="panel">
        <header class="panel-header compact">
          <div>
            <h2>费用结构</h2>
            <span>本期累计</span>
          </div>
          <small>单位：元</small>
        </header>
        <div class="expense-legend">
          <span v-for="item in expenseLegend" :key="item.name">
            <i :style="{ background: item.color }"></i>{{ item.name }}
          </span>
        </div>
        <div class="stack-list">
          <div v-for="row in expenseRows" :key="row.store">
            <span>{{ row.store }}</span>
            <div class="stack-bar">
              <i
                v-for="seg in row.segments"
                :key="seg.name"
                :style="{ width: `${seg.value}%`, background: seg.color }"
              >
                {{ seg.value }}%
              </i>
            </div>
          </div>
        </div>
      </article>

      <article class="panel">
        <header class="panel-header compact">
          <div>
            <h2>菜品贡献 TOP10</h2>
            <span>本期累计</span>
          </div>
          <button type="button" class="text-link">更多</button>
        </header>
        <table class="finance-table product-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>菜品名称</th>
              <th>营业收入</th>
              <th>毛利率</th>
              <th>占比</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in productRows" :key="item.name">
              <td><span class="rank-dot">{{ item.rank }}</span></td>
              <td>{{ item.name }}</td>
              <td>{{ compactCurrency(item.revenue) }}</td>
              <td>{{ item.margin }}</td>
              <td>{{ item.share }}</td>
            </tr>
          </tbody>
        </table>
      </article>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw, nextTick, onMounted, ref, type Component } from 'vue'
import {
  Coin,
  DataLine,
  Goods,
  Histogram,
  Money,
  RefreshRight,
  Search,
  Sell,
  Tickets,
  TrendCharts,
  Upload,
  Wallet,
} from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

import StoreSelect from '@/components/StoreSelect.vue'
import { useECharts, type ECOption } from '@/composables/useECharts'
import { getDashboardOverview } from '@/api/dashboard'
import { rebuildKPI } from '@/api/kpi'
import { DEMO_PERIOD, PERMISSIONS } from '@/config'
import type { StoreRankItem, SummaryCard } from '@/types'

type QuickRange = 'demo' | 'today' | 'week' | 'last_month' | 'month' | 'custom'

interface DashboardCard {
  key: string
  label: string
  display: string
  mom: number | null
  yoy: number | null
  isPoint?: boolean
  icon: Component
  tone: string
  spark: number[]
}

const RED = '#C81E1E'
const GREEN = '#2F8F5B'
const GOLD = '#D19A36'
const INK = '#332D28'
const MUTED = '#756D64'

const storeId = ref<number | undefined>(undefined)
const quickRange = ref<QuickRange>('demo')
const customDateRange = ref<[string, string]>()
const rebuildLoading = ref(false)
const updatedAt = ref('2024-06-01 08:30')
const waterfallMode = ref('图形')

const summaryCards = ref<SummaryCard[]>([])
const storeRanking = ref<StoreRankItem[]>([])
const expenseTotal = ref(427350)
const profitRate = ref(12.57)

const waterfallChartRef = ref<HTMLElement | null>(null)
const { setOption: setWaterfallOption, showLoading, hideLoading } = useECharts(waterfallChartRef)

const fallbackCards: SummaryCard[] = [
  { label: '营业收入', value: 2485630, unit: '元', yoy_growth: 18.3, mom_growth: 12.6 },
  { label: '净利润', value: 312540, unit: '元', yoy_growth: 23.7, mom_growth: 15.4 },
  { label: '订单总数', value: 18732, unit: '单', yoy_growth: 16.5, mom_growth: 8.7 },
  { label: '客单价', value: 132.59, unit: '元', yoy_growth: 1.6, mom_growth: 3.6 },
  { label: '利润率', value: 12.57, unit: '%', yoy_growth: 0.44, mom_growth: 0.28 },
  { label: '预算执行率', value: 86.2, unit: '%', yoy_growth: null, mom_growth: -2.3 },
]

const fallbackStores: StoreRankItem[] = [
  { store_name: '朝阳大悦城店', revenue: 386540, profit: 56780 },
  { store_name: '海淀中关村店', revenue: 325210, profit: 46120 },
  { store_name: '西城金融街店', revenue: 298760, profit: 38450 },
  { store_name: '望京凯德店', revenue: 245310, profit: 29670 },
  { store_name: '东直门来福士店', revenue: 198430, profit: 22340 },
  { store_name: '五道口店', revenue: 176880, profit: 19850 },
  { store_name: '国贸商城店', revenue: 168920, profit: 18620 },
  { store_name: '合生汇店', revenue: 146730, profit: 14710 },
]

const productRows = [
  { rank: 1, name: '水煮牛肉', revenue: 156320, margin: '58.6%', share: '14.7%' },
  { rank: 2, name: '烤鸭', revenue: 142850, margin: '62.1%', share: '14.3%' },
  { rank: 3, name: '宫保鸡丁', revenue: 98760, margin: '55.7%', share: '8.8%' },
  { rank: 4, name: '酸菜鱼', revenue: 92650, margin: '53.2%', share: '7.9%' },
  { rank: 5, name: '麻婆豆腐', revenue: 78430, margin: '50.6%', share: '6.4%' },
  { rank: 6, name: '干锅花菜', revenue: 65210, margin: '48.9%', share: '5.1%' },
  { rank: 7, name: '蒜蓉生菜', revenue: 52130, margin: '46.2%', share: '4.0%' },
]

const expenseLegend = [
  { name: '人工成本', color: RED },
  { name: '租金及物业', color: GOLD },
  { name: '能源费用', color: GREEN },
  { name: '营销费用', color: '#E67D1F' },
  { name: '其他费用', color: '#7A8289' },
]

const expenseRows = computed(() => {
  return fallbackStores.slice(0, 7).map((store, index) => ({
    store: store.store_name,
    segments: [
      { name: '人工成本', value: 27 - (index % 4), color: RED },
      { name: '租金及物业', value: 18 + (index % 3), color: GOLD },
      { name: '能源费用', value: 7, color: GREEN },
      { name: '营销费用', value: 21 - (index % 3), color: '#E67D1F' },
      { name: '其他费用', value: 27 + (index % 5), color: '#7A8289' },
    ],
  }))
})

const riskAlerts = computed(() => [
  {
    title: '毛利异常',
    content: `当前毛利率 ${profitRate.value.toFixed(1)}%，较目标下滑 5.2 pct`,
    level: '高',
    levelClass: 'high',
    time: '今天 08:12',
    tone: 'red',
    icon: markRaw(TrendCharts),
  },
  {
    title: '费用超标',
    content: `营销费用 ${compactCurrency(expenseTotal.value * 0.28)}，超预算 12.3%`,
    level: '中',
    levelClass: 'mid',
    time: '今天 07:45',
    tone: 'gold',
    icon: markRaw(Wallet),
  },
  {
    title: '库存周转',
    content: '库存周转天数 18 天，高于行业均值 14 天',
    level: '中',
    levelClass: 'mid',
    time: '昨天 18:20',
    tone: 'green',
    icon: markRaw(Goods),
  },
  {
    title: '数据导入',
    content: '有 2 家门店未完成昨日数据导入',
    level: '低',
    levelClass: 'low',
    time: '昨天 17:10',
    tone: 'slate',
    icon: markRaw(Upload),
  },
])

const dashboardCards = computed<DashboardCard[]>(() => {
  const source = summaryCards.value.length ? summaryCards.value : fallbackCards
  const iconMap: Record<string, Component> = {
    营业收入: markRaw(DataLine),
    净利润: markRaw(Coin),
    利润: markRaw(Coin),
    订单总数: markRaw(Tickets),
    客单价: markRaw(Sell),
    利润率: markRaw(Histogram),
    预算执行率: markRaw(Wallet),
    门店数: markRaw(Money),
  }
  const tones = ['red', 'gold', 'red', 'red', 'gold', 'gold']

  return source.slice(0, 6).map((card, index) => ({
    key: `${card.label}-${index}`,
    label: card.label === '利润' ? '净利润' : card.label,
    display: formatCardValue(card),
    mom: card.mom_growth,
    yoy: card.yoy_growth,
    isPoint: card.unit === '%',
    icon: iconMap[card.label] || markRaw(Money),
    tone: tones[index] || 'red',
    spark: sparkFor(index, card.mom_growth ?? 0),
  }))
})

const storeRows = computed(() => {
  return (storeRanking.value.length ? storeRanking.value : fallbackStores).slice(0, 8)
})

const storeTotal = computed(() => {
  return storeRows.value.reduce(
    (sum, row) => ({
      revenue: sum.revenue + row.revenue,
      profit: sum.profit + row.profit,
    }),
    { revenue: 0, profit: 0 }
  )
})

function formatCardValue(card: SummaryCard): string {
  if (card.unit === '元') return `¥ ${Number(card.value).toLocaleString('zh-CN', { maximumFractionDigits: 2 })}`
  if (card.unit === '%') return `${Number(card.value).toFixed(2)}%`
  return `${Math.round(card.value).toLocaleString('zh-CN')} ${card.unit || ''}`.trim()
}

function compactCurrency(value: number): string {
  return value.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}

function ratio(part: number, total: number): string {
  if (!total) return '0.00%'
  return `${((part / total) * 100).toFixed(2)}%`
}

function trendClass(value: number | null): string {
  if (value === null || value === undefined) return 'neutral'
  return value >= 0 ? 'positive' : 'negative'
}

function formatTrend(value: number | null, isPoint = false): string {
  if (value === null || value === undefined) return '--'
  const prefix = value >= 0 ? '↑' : '↓'
  const suffix = isPoint ? ' pct' : '%'
  return `${prefix} ${Math.abs(value).toFixed(isPoint ? 2 : 1)}${suffix}`
}

function sparkFor(index: number, trend: number): number[] {
  const up = trend >= 0
  const presets = [
    [26, 34, 24, 42, 30, 48, 38, 58, 45, 30, 50, 32],
    [22, 38, 45, 40, 31, 44, 61, 35, 48, 39, 52, 34],
    [20, 24, 45, 35, 40, 62, 32, 43, 39, 50, 66, 42],
    [24, 36, 31, 48, 54, 35, 28, 46, 34, 26, 38, 32],
  ]
  const values = presets[index % presets.length]
  return up ? values : [...values].reverse()
}

function getDateRange(): { start_date: string; end_date: string } {
  const today = dayjs()
  switch (quickRange.value) {
    case 'demo':
      return { start_date: DEMO_PERIOD.startDate, end_date: DEMO_PERIOD.endDate }
    case 'today':
      return { start_date: today.format('YYYY-MM-DD'), end_date: today.format('YYYY-MM-DD') }
    case 'week': {
      const monday = today.startOf('week').add(1, 'day')
      return { start_date: monday.format('YYYY-MM-DD'), end_date: today.format('YYYY-MM-DD') }
    }
    case 'last_month': {
      const lastMonth = today.subtract(1, 'month')
      return {
        start_date: lastMonth.startOf('month').format('YYYY-MM-DD'),
        end_date: lastMonth.endOf('month').format('YYYY-MM-DD'),
      }
    }
    case 'month':
      return { start_date: today.startOf('month').format('YYYY-MM-DD'), end_date: today.format('YYYY-MM-DD') }
    case 'custom':
      if (customDateRange.value?.length === 2) {
        return { start_date: customDateRange.value[0], end_date: customDateRange.value[1] }
      }
      return { start_date: today.startOf('month').format('YYYY-MM-DD'), end_date: today.format('YYYY-MM-DD') }
  }
}

function hasBusinessData(cards: SummaryCard[], stores: StoreRankItem[]): boolean {
  return cards.some(card => Math.abs(Number(card.value || 0)) > 0) || stores.length > 0
}

function handleQuickRangeChange() {
  if (quickRange.value !== 'custom') {
    fetchData()
  }
}

async function fetchData() {
  const range = getDateRange()
  showLoading()

  try {
    const res = await getDashboardOverview({
      ...range,
      store_id: storeId.value,
    })

    if ((res.code === 0 || res.code === 200) && res.data) {
      const cards = res.data.summary_cards || []
      const stores = res.data.store_ranking || []
      if (hasBusinessData(cards, stores)) {
        summaryCards.value = cards
        storeRanking.value = stores
        expenseTotal.value = (res.data.expense_structure || []).reduce((sum, item) => sum + item.value, 0) || expenseTotal.value
        profitRate.value = res.data.profit_rate || profitRate.value
        updatedAt.value = dayjs().format('YYYY-MM-DD HH:mm')
      } else {
        applyFallback()
      }
    } else {
      applyFallback()
    }
  } catch {
    ElMessage.error('加载仪表盘数据失败，已显示本地经营样例')
    applyFallback()
  } finally {
    renderWaterfall()
    hideLoading()
  }
}

function applyFallback() {
  summaryCards.value = fallbackCards
  storeRanking.value = fallbackStores
  expenseTotal.value = 427350
  profitRate.value = 12.57
  updatedAt.value = '2024-06-01 08:30'
}

function renderWaterfall() {
  const revenue = findMetric(['营业收入']) || 2485630
  const profit = findMetric(['净利润', '利润']) || 312540
  const materialCost = -Math.round(revenue * 0.528)
  const grossProfit = revenue + materialCost
  const laborCost = -Math.round(revenue * 0.166)
  const rentCost = -Math.round(revenue * 0.056)
  const energyCost = -Math.round(revenue * 0.035)
  const marketingCost = -Math.round(revenue * 0.026)
  const otherCost = profit - (grossProfit + laborCost + rentCost + energyCost + marketingCost)
  const items = [
    { name: '营业收入', value: revenue, type: 'increase' },
    { name: '营业成本', value: materialCost, type: 'decrease' },
    { name: '毛利', value: grossProfit, type: 'total' },
    { name: '人工成本', value: laborCost, type: 'decrease' },
    { name: '租金及物业', value: rentCost, type: 'decrease' },
    { name: '能源费用', value: energyCost, type: 'decrease' },
    { name: '营销费用', value: marketingCost, type: 'decrease' },
    { name: '其他费用', value: otherCost, type: 'decrease' },
    { name: '净利润', value: profit, type: 'final' },
  ]

  let running = 0
  const bases: number[] = []
  const values: number[] = []
  const colors: string[] = []

  items.forEach((item) => {
    if (item.type === 'final') {
      bases.push(0)
      values.push(item.value)
      colors.push(RED)
      return
    }

    if (item.value >= 0) {
      bases.push(item.type === 'total' ? 0 : running)
      values.push(item.type === 'total' ? item.value : item.value)
      colors.push(item.type === 'total' ? GOLD : RED)
    } else {
      bases.push(running + item.value)
      values.push(Math.abs(item.value))
      colors.push(GREEN)
    }

    running = item.type === 'total' ? item.value : running + item.value
  })

  const option: ECOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: unknown) => {
        const list = Array.isArray(params) ? params : []
        const visible = list.find((item) => (item as { seriesName?: string }).seriesName === '金额') as
          | { name?: string; dataIndex?: number }
          | undefined
        if (!visible || visible.dataIndex === undefined) return ''
        const item = items[visible.dataIndex]
        return `<strong>${visible.name}</strong><br/>${item.value >= 0 ? '+' : '-'} ¥${Math.abs(item.value).toLocaleString('zh-CN')}`
      },
    },
    grid: { left: 54, right: 24, top: 28, bottom: 54 },
    xAxis: {
      type: 'category',
      data: items.map(item => item.name),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: '#D7CEC2' } },
      axisLabel: { color: MUTED, fontSize: 12 },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: MUTED,
        formatter: (value: number) => `${Math.round(value / 10000)}万`,
      },
      splitLine: { lineStyle: { color: '#EEE7DC' } },
    },
    series: [
      {
        name: 'base',
        type: 'bar',
        stack: 'total',
        itemStyle: { color: 'transparent' },
        emphasis: { disabled: true },
        data: bases,
      },
      {
        name: '金额',
        type: 'bar',
        stack: 'total',
        barWidth: 42,
        data: values.map((value, index) => ({
          value,
          itemStyle: { color: colors[index], borderRadius: [3, 3, 0, 0] },
        })),
        label: {
          show: true,
          position: 'top',
          color: INK,
          fontSize: 11,
          formatter: (params: { dataIndex: number }) => {
            const item = items[params.dataIndex]
            return `${item.value < 0 ? '-' : ''}${Math.abs(item.value).toLocaleString('zh-CN')}`
          },
        },
      },
    ],
  }

  setWaterfallOption(option, true)
}

function findMetric(labels: string[]): number | null {
  const source = summaryCards.value.length ? summaryCards.value : fallbackCards
  const found = source.find(item => labels.includes(item.label))
  return found ? found.value : null
}

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
    ElMessage.success(`重建成功！影响 ${data.total_records} 条记录`)
    await fetchData()
  } catch (error: unknown) {
    if (error !== 'cancel') {
      ElMessage.error('重建 KPI 失败')
    }
  } finally {
    rebuildLoading.value = false
  }
}

onMounted(async () => {
  await nextTick()
  applyFallback()
  renderWaterfall()
  fetchData()
})
</script>

<style scoped lang="scss">
.dashboard-page {
  display: grid;
  gap: 10px;
}

.dashboard-toolbar {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-end;
  margin-bottom: 2px;

  h1 {
    margin: 2px 0 0;
    font-size: 22px;
    font-weight: 900;
    color: #211A15;
  }
}

.eyebrow {
  margin: 0;
  color: #8A8074;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
}

.toolbar-controls {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-wrap: wrap;
}

.custom-date {
  width: 260px;
}

.ghost-action {
  background: #FFFDF9;
  border-color: #D7CEC2;
  color: #332D28;
}

.data-freshness {
  justify-self: end;
  color: #8A8074;
  font-size: 12px;
  margin-bottom: 2px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.metric-card,
.panel {
  background: rgba(255, 253, 249, 0.96);
  border: 1px solid #E5DED4;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
}

.metric-card {
  min-height: 184px;
  padding: 16px 10px 12px;
  position: relative;
  overflow: hidden;
}

.metric-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  color: #332D28;
  font-size: 15px;
  font-weight: 900;

  .el-icon {
    font-size: 20px;

    &.red {
      color: #C81E1E;
    }

    &.gold {
      color: #D19A36;
    }
  }
}

.metric-value {
  margin-top: 16px;
  color: #17110D;
  font-size: 26px;
  font-weight: 900;
  line-height: 1;
  white-space: nowrap;
}

.metric-trends {
  margin-top: 18px;
  display: grid;
  gap: 7px;
  color: #756D64;
  font-size: 12px;

  b {
    margin-left: 8px;
  }
}

.positive {
  color: #2F8F5B;
}

.negative {
  color: #C81E1E;
}

.neutral {
  color: #8A8074;
}

.spark-bars {
  position: absolute;
  inset: auto 16px 12px 16px;
  height: 30px;
  display: flex;
  align-items: flex-end;
  gap: 5px;
  opacity: 0.72;

  i {
    flex: 1;
    min-width: 3px;
    border-radius: 999px 999px 0 0;
    background: linear-gradient(180deg, #C81E1E, rgba(200, 30, 30, 0.12));
  }
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(360px, 0.8fr);
  gap: 10px;
  margin-top: 10px;
}

.lower-grid {
  display: grid;
  grid-template-columns: 1.04fr 1.06fr 1.14fr;
  gap: 10px;
  margin-top: 10px;
}

.panel {
  min-width: 0;
  padding: 14px;
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid #EEE7DC;

  h2 {
    margin: 0;
    color: #211A15;
    font-size: 16px;
    font-weight: 900;
  }

  span,
  small {
    color: #8A8074;
    font-size: 12px;
    font-weight: 700;
  }

  &.compact {
    padding-bottom: 8px;
  }
}

.panel-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.text-link {
  border: 0;
  background: transparent;
  color: #756D64;
  cursor: pointer;
  font-weight: 800;

  &:hover {
    color: #C81E1E;
  }
}

.waterfall-chart {
  width: 100%;
  height: 320px;
}

.risk-table {
  display: grid;
}

.risk-row {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr) 52px 76px;
  gap: 12px;
  align-items: center;
  min-height: 58px;
  border-bottom: 1px solid #F0E9DF;
  color: #554D46;
  font-size: 13px;

  &:last-child {
    border-bottom: 0;
  }

  &.risk-head {
    min-height: 36px;
    color: #8A8074;
    font-size: 12px;
    font-weight: 900;
  }
}

.risk-type {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #332D28;
  font-weight: 900;

  i {
    display: grid;
    place-items: center;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    color: #fff;
    font-style: normal;

    &.red {
      background: #C81E1E;
    }

    &.gold {
      background: #D98F20;
    }

    &.green {
      background: #2F8F5B;
    }

    &.slate {
      background: #657078;
    }
  }
}

.risk-badge {
  display: inline-grid;
  place-items: center;
  min-width: 30px;
  height: 28px;
  border-radius: 6px;
  font-size: 12px;

  &.high {
    color: #C81E1E;
    background: #FFE7E1;
  }

  &.mid {
    color: #A96711;
    background: #FFF0D4;
  }

  &.low {
    color: #554D46;
    background: #EEEAE3;
  }
}

.finance-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  color: #554D46;

  th,
  td {
    padding: 9px 8px;
    border-bottom: 1px solid #F0E9DF;
    text-align: right;
    white-space: nowrap;
  }

  th {
    color: #8A8074;
    font-weight: 900;
  }

  th:nth-child(2),
  td:nth-child(2) {
    text-align: left;
  }

  tfoot td {
    color: #211A15;
    font-weight: 900;
    border-bottom: 0;
  }
}

.rank-dot {
  display: inline-grid;
  place-items: center;
  min-width: 19px;
  height: 19px;
  border-radius: 50%;
  background: #E8DCC9;
  color: #7A4E0D;
  font-size: 11px;
  font-weight: 900;
}

.expense-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 12px 0 16px;
  color: #695F55;
  font-size: 12px;
  font-weight: 800;

  span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  i {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }
}

.stack-list {
  display: grid;
  gap: 12px;
  font-size: 12px;

  > div {
    display: grid;
    grid-template-columns: 100px minmax(0, 1fr);
    align-items: center;
    gap: 10px;
  }

  > div > span {
    color: #554D46;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.stack-bar {
  display: flex;
  height: 22px;
  border-radius: 3px;
  overflow: hidden;
  background: #EFE7DC;

  i {
    display: grid;
    place-items: center;
    min-width: 24px;
    color: #fff;
    font-style: normal;
    font-size: 10px;
    font-weight: 900;
  }
}

.product-table {
  th,
  td {
    padding-top: 8px;
    padding-bottom: 8px;
  }
}

@media (max-width: 1320px) {
  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .dashboard-grid,
  .lower-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .dashboard-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .toolbar-controls {
    justify-content: flex-start;
  }

  .metric-grid {
    grid-template-columns: 1fr;
  }

  .risk-row {
    grid-template-columns: 1fr;
    gap: 4px;
    padding: 10px 0;

    &.risk-head {
      display: none;
    }
  }

  .finance-table {
    display: block;
    overflow-x: auto;
  }
}
</style>
