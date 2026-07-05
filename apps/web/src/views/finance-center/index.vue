<template>
  <div class="finance-center-page">
    <section class="finance-center-toolbar">
      <div>
        <p class="eyebrow">Finance Operating Center</p>
        <h1>财务运营中心</h1>
      </div>

      <div class="toolbar-controls">
        <el-radio-group v-model="viewMode" size="small" @change="handleViewModeChange">
          <el-radio-button value="overview">运营总览</el-radio-button>
          <el-radio-button value="close">关账准备</el-radio-button>
        </el-radio-group>
        <StoreSelect v-model="storeId" width="156px" />
        <el-radio-group v-model="quickRange" size="small" @change="handleQuickRangeChange">
          <el-radio-button value="demo">演示月</el-radio-button>
          <el-radio-button value="month">本月</el-radio-button>
          <el-radio-button value="last_month">上月</el-radio-button>
          <el-radio-button value="quarter">本季</el-radio-button>
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
        <el-button type="primary" :icon="Search" :loading="loading" @click="fetchActiveView">
          查询
        </el-button>
        <el-tooltip content="刷新当前财务视图" placement="top">
          <el-button :icon="RefreshRight" circle :loading="loading" @click="fetchActiveView" />
        </el-tooltip>
      </div>
    </section>

    <div class="freshness-line">
      <span>数据生成：{{ activeGeneratedAtLabel }}</span>
      <span>{{ activeMethodology }}</span>
    </div>

    <template v-if="viewMode === 'overview'">
      <section class="finance-card-grid">
        <article v-for="card in cards" :key="card.key" :class="['finance-card', card.tone]">
          <div class="card-top">
            <span>{{ card.label }}</span>
            <el-icon><component :is="cardIcon(card.key)" /></el-icon>
          </div>
          <strong class="font-number">{{ formatMetric(card.value, card.unit) }}</strong>
          <p>{{ card.description }}</p>
        </article>
      </section>

      <section class="finance-main-grid">
        <article class="panel panel-wide">
          <header class="panel-header">
            <div>
              <h2>现金流压力曲线</h2>
              <span>流入、流出与累计净现金流</span>
            </div>
            <small>单位：元</small>
          </header>
          <div ref="cashFlowChartRef" class="cashflow-chart"></div>
        </article>

        <article class="panel">
          <header class="panel-header">
            <div>
              <h2>优先行动清单</h2>
              <span>根据资金、预算与往来款自动生成</span>
            </div>
          </header>
          <div class="action-list">
            <div v-for="item in actionItems" :key="item.title" class="action-item">
              <b :class="priorityClass(item.priority)">{{ item.priority }}</b>
              <div>
                <strong>{{ item.title }}</strong>
                <p>{{ item.reason }}</p>
                <span>{{ item.owner }} · {{ item.due_hint }}</span>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="finance-lower-grid">
        <article class="panel">
          <header class="panel-header compact">
            <div>
              <h2>往来与结算风险</h2>
              <span>应收、待结算、应付</span>
            </div>
          </header>
          <div class="capital-list">
            <div v-for="item in workingCapital" :key="item.key" class="capital-item">
              <div>
                <strong>{{ item.name }}</strong>
                <span>{{ item.count }} 条记录</span>
              </div>
              <b class="font-number">{{ money(item.amount) }}</b>
              <el-tag :type="riskTag(item.risk_level)" effect="plain">{{ riskLabel(item.risk_level) }}</el-tag>
              <p>{{ item.suggestion }}</p>
            </div>
          </div>
        </article>

        <article class="panel">
          <header class="panel-header compact">
            <div>
              <h2>预算控制排行</h2>
              <span>按执行率降序</span>
            </div>
          </header>
          <table class="finance-table">
            <thead>
              <tr>
                <th>科目</th>
                <th>实际</th>
                <th>预算</th>
                <th>执行率</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in budgetControls" :key="item.name">
                <td>{{ item.name }}</td>
                <td>{{ money(item.actual) }}</td>
                <td>{{ money(item.budget) }}</td>
                <td>{{ item.execution_rate.toFixed(1) }}%</td>
                <td><el-tag :type="budgetTag(item.status)" effect="plain">{{ budgetLabel(item.status) }}</el-tag></td>
              </tr>
            </tbody>
          </table>
        </article>

        <article class="panel panel-capability">
          <header class="panel-header compact">
            <div>
              <h2>扩展功能成熟度</h2>
              <span>结合真实财务系统要求与当前项目能力</span>
            </div>
          </header>
          <div class="capability-list">
            <div v-for="item in capabilityMatrix" :key="item.key" class="capability-item">
              <div class="capability-head">
                <div>
                  <strong>{{ item.name }}</strong>
                  <span>{{ item.category }}</span>
                </div>
                <el-tag :type="capabilityTag(item.status)" effect="plain">
                  {{ capabilityLabel(item.status) }}
                </el-tag>
              </div>
              <el-progress
                :percentage="item.maturity_score"
                :stroke-width="8"
                :color="progressColor(item.status)"
              />
              <p>{{ item.current_support }}</p>
              <div class="next-actions">
                <span v-for="action in item.next_actions.slice(0, 3)" :key="action">{{ action }}</span>
              </div>
            </div>
          </div>
        </article>
      </section>
    </template>

    <template v-else>
      <section class="close-score-band">
        <article class="panel score-panel">
          <div>
            <span>关账准备评分</span>
            <strong class="font-number">{{ closeScore }}</strong>
          </div>
          <el-progress
            :percentage="closeScore"
            :stroke-width="10"
            :color="closeScoreColor"
          />
          <p>{{ closePeriodLabel }}</p>
        </article>
        <article v-for="item in closeStats" :key="item.label" class="panel close-stat">
          <span>{{ item.label }}</span>
          <strong class="font-number">{{ item.value }}</strong>
          <p>{{ item.hint }}</p>
        </article>
      </section>

      <section class="close-check-grid">
        <article
          v-for="item in closeChecklist"
          :key="item.key"
          :class="['panel', 'close-check-card', item.status]"
        >
          <div class="close-check-head">
            <div>
              <strong>{{ item.name }}</strong>
              <span>{{ item.owner }}</span>
            </div>
            <el-tag :type="closeStatusTag(item.status)" effect="plain">{{ closeStatusLabel(item.status) }}</el-tag>
          </div>
          <div class="close-check-metrics">
            <span>已就绪 {{ item.ready_count }}</span>
            <span>待处理 {{ item.issue_count }}</span>
            <span>{{ money(item.amount) }}</span>
          </div>
          <p>{{ item.description }}</p>
          <small>{{ item.next_step }}</small>
        </article>
      </section>

      <section class="close-main-grid">
        <article class="panel">
          <header class="panel-header compact">
            <div>
              <h2>银行对账准备</h2>
              <span>按收付款通道识别缺口</span>
            </div>
          </header>
          <table class="finance-table close-bank-table">
            <thead>
              <tr>
                <th>通道</th>
                <th>方向</th>
                <th>应对账金额</th>
                <th>记录数</th>
                <th>未匹配</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!bankReconciliation.length">
                <td colspan="6" class="table-empty">暂无可对账收付款通道</td>
              </tr>
              <tr v-for="item in bankReconciliation" :key="`${item.direction}-${item.channel}`">
                <td>
                  <strong>{{ item.channel }}</strong>
                  <span>{{ item.account_hint }}</span>
                </td>
                <td>{{ directionLabel(item.direction) }}</td>
                <td>{{ money(item.expected_amount) }}</td>
                <td>{{ item.record_count }}</td>
                <td>{{ item.unmatched_count }} / {{ money(item.unmatched_amount) }}</td>
                <td><el-tag :type="closeStatusTag(item.status)" effect="plain">{{ closeStatusLabel(item.status) }}</el-tag></td>
              </tr>
            </tbody>
          </table>
        </article>

        <article class="panel">
          <header class="panel-header compact">
            <div>
              <h2>总账底稿准备</h2>
              <span>从经营数据走向核算闭环</span>
            </div>
          </header>
          <div class="ledger-list">
            <div v-for="item in ledgerReadiness" :key="item.key" class="ledger-item">
              <div>
                <strong>{{ item.name }}</strong>
                <span>{{ item.source }}</span>
              </div>
              <el-progress
                :percentage="item.coverage"
                :stroke-width="8"
                :color="closeProgressColor(item.status)"
              />
              <el-tag :type="closeStatusTag(item.status)" effect="plain">{{ closeStatusLabel(item.status) }}</el-tag>
              <p>{{ item.remark }}</p>
            </div>
          </div>
        </article>

        <article class="panel">
          <header class="panel-header compact">
            <div>
              <h2>关账行动清单</h2>
              <span>优先处理会阻断关账的问题</span>
            </div>
          </header>
          <div class="action-list">
            <div v-for="item in closeActionItems" :key="item.title" class="action-item">
              <b :class="priorityClass(item.priority)">{{ item.priority }}</b>
              <div>
                <strong>{{ item.title }}</strong>
                <p>{{ item.reason }}</p>
                <span>{{ item.owner }} · {{ item.due_hint }}</span>
              </div>
            </div>
          </div>
        </article>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw, nextTick, onMounted, ref, type Component } from 'vue'
import dayjs from 'dayjs'
import {
  Clock,
  Money,
  RefreshRight,
  Search,
  Tickets,
  TrendCharts,
  Wallet,
  Warning,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import StoreSelect from '@/components/StoreSelect.vue'
import { getFinanceCloseReadiness, getFinanceOperationsOverview } from '@/api/finance'
import { DEMO_PERIOD } from '@/config'
import { useECharts, type ECOption } from '@/composables/useECharts'
import type {
  BankReconciliationItem,
  BudgetControlItem,
  CashFlowPoint,
  FinanceActionItem,
  FinanceCapability,
  FinanceCloseChecklistItem,
  FinanceMetricCard,
  LedgerReadinessItem,
  WorkingCapitalItem,
} from '@/types'

type QuickRange = 'demo' | 'month' | 'last_month' | 'quarter' | 'custom'
type ViewMode = 'overview' | 'close'

const RED = '#C81E1E'
const GREEN = '#2F8F5B'
const GOLD = '#D19A36'
const MUTED = '#756D64'

const storeId = ref<number | undefined>(undefined)
const viewMode = ref<ViewMode>('overview')
const quickRange = ref<QuickRange>('demo')
const customDateRange = ref<[string, string]>()
const loading = ref(false)
const generatedAt = ref('')
const closeGeneratedAt = ref('')
const closeScore = ref(0)
const closePeriod = ref({ start: '', end: '' })

const cards = ref<FinanceMetricCard[]>([])
const cashFlow = ref<CashFlowPoint[]>([])
const workingCapital = ref<WorkingCapitalItem[]>([])
const budgetControls = ref<BudgetControlItem[]>([])
const capabilityMatrix = ref<FinanceCapability[]>([])
const actionItems = ref<FinanceActionItem[]>([])
const closeChecklist = ref<FinanceCloseChecklistItem[]>([])
const bankReconciliation = ref<BankReconciliationItem[]>([])
const ledgerReadiness = ref<LedgerReadinessItem[]>([])
const closeActionItems = ref<FinanceActionItem[]>([])

const cashFlowChartRef = ref<HTMLElement | null>(null)
const { setOption: setCashFlowOption, showLoading, hideLoading } = useECharts(cashFlowChartRef)

const generatedAtLabel = computed(() => {
  return generatedAt.value ? dayjs(generatedAt.value).format('YYYY-MM-DD HH:mm') : '本地样例'
})

const closeGeneratedAtLabel = computed(() => {
  return closeGeneratedAt.value ? dayjs(closeGeneratedAt.value).format('YYYY-MM-DD HH:mm') : '本地样例'
})

const activeGeneratedAtLabel = computed(() => {
  return viewMode.value === 'overview' ? generatedAtLabel.value : closeGeneratedAtLabel.value
})

const activeMethodology = computed(() => {
  if (viewMode.value === 'overview') {
    return '口径：订单净额、已审批/已支付费用、费用预算'
  }
  return '口径：收付款时间、费用状态、导入批次、预算与审计日志'
})

const closeScoreColor = computed(() => {
  if (closeScore.value >= 86) return GREEN
  if (closeScore.value >= 70) return GOLD
  return RED
})

const closePeriodLabel = computed(() => {
  const start = closePeriod.value.start || getDateRange().start_date
  const end = closePeriod.value.end || getDateRange().end_date
  return `${start} ~ ${end}`
})

const closeStats = computed(() => {
  const blockers = closeChecklist.value.filter(item => item.status === 'blocker').length
  const warnings = closeChecklist.value.filter(item => item.status === 'warning').length
  const issueAmount = closeChecklist.value.reduce((sum, item) => sum + Number(item.amount || 0), 0)
  return [
    { label: '阻断项', value: blockers, hint: '需要先处理再进入正式关账' },
    { label: '关注项', value: warnings, hint: '不一定阻断，但会影响底稿质量' },
    { label: '待处理金额', value: money(issueAmount), hint: '来自收入、费用和付款截止检查' },
  ]
})

function getDateRange() {
  const today = dayjs()
  if (quickRange.value === 'demo') {
    return {
      start_date: DEMO_PERIOD.startDate,
      end_date: DEMO_PERIOD.endDate,
    }
  }
  if (quickRange.value === 'last_month') {
    const lastMonth = today.subtract(1, 'month')
    return {
      start_date: lastMonth.startOf('month').format('YYYY-MM-DD'),
      end_date: lastMonth.endOf('month').format('YYYY-MM-DD'),
    }
  }
  if (quickRange.value === 'quarter') {
    const quarterStartMonth = Math.floor(today.month() / 3) * 3
    return {
      start_date: today.month(quarterStartMonth).startOf('month').format('YYYY-MM-DD'),
      end_date: today.format('YYYY-MM-DD'),
    }
  }
  if (quickRange.value === 'custom' && customDateRange.value?.length === 2) {
    return {
      start_date: customDateRange.value[0],
      end_date: customDateRange.value[1],
    }
  }
  return {
    start_date: today.startOf('month').format('YYYY-MM-DD'),
    end_date: today.format('YYYY-MM-DD'),
  }
}

function hasOperationsData(data: {
  cards?: FinanceMetricCard[]
  cash_flow?: CashFlowPoint[]
  working_capital?: WorkingCapitalItem[]
  budget_controls?: BudgetControlItem[]
}) {
  const hasCards = (data.cards || []).some(item => Math.abs(Number(item.value || 0)) > 0)
  const hasCashFlow = (data.cash_flow || []).some(item =>
    Math.abs(Number(item.inflow || 0)) + Math.abs(Number(item.outflow || 0)) + Math.abs(Number(item.cumulative || 0)) > 0
  )
  const hasCapital = (data.working_capital || []).some(item => Math.abs(Number(item.amount || 0)) > 0)
  const hasBudget = (data.budget_controls || []).some(item => Math.abs(Number(item.actual || 0)) + Math.abs(Number(item.budget || 0)) > 0)
  return hasCards || hasCashFlow || hasCapital || hasBudget
}

function hasCloseData(data: {
  close_score?: number
  checklist?: FinanceCloseChecklistItem[]
  bank_reconciliation?: BankReconciliationItem[]
}) {
  const hasChecklist = (data.checklist || []).some(item =>
    Number(item.issue_count || 0) > 0 || Math.abs(Number(item.amount || 0)) > 0
  )
  const hasBank = (data.bank_reconciliation || []).some(item =>
    Number(item.record_count || 0) > 0 || Math.abs(Number(item.expected_amount || 0)) > 0
  )
  return Number(data.close_score || 0) > 0 || hasChecklist || hasBank
}

function handleQuickRangeChange() {
  if (quickRange.value !== 'custom') {
    fetchActiveView()
  }
}

async function handleViewModeChange() {
  await nextTick()
  if (viewMode.value === 'overview') {
    renderCashFlow()
  }
  fetchActiveView()
}

function fetchActiveView() {
  if (viewMode.value === 'close') {
    return fetchCloseReadiness()
  }
  return fetchOverview()
}

async function fetchOverview() {
  const range = getDateRange()
  loading.value = true
  showLoading()
  try {
    const response = await getFinanceOperationsOverview({
      ...range,
      store_id: storeId.value,
    })
    if ((response.code === 0 || response.code === 200) && response.data) {
      if (hasOperationsData(response.data)) {
        cards.value = response.data.cards
        cashFlow.value = response.data.cash_flow
        workingCapital.value = response.data.working_capital
        budgetControls.value = response.data.budget_controls
        capabilityMatrix.value = response.data.capability_matrix
        actionItems.value = response.data.action_items
        generatedAt.value = response.data.generated_at
      } else {
        applyFallback()
      }
    } else {
      applyFallback()
    }
  } catch {
    ElMessage.warning('财务运营接口暂不可用，已显示本地样例')
    applyFallback()
  } finally {
    await nextTick()
    renderCashFlow()
    hideLoading()
    loading.value = false
  }
}

async function fetchCloseReadiness() {
  const range = getDateRange()
  loading.value = true
  try {
    const response = await getFinanceCloseReadiness({
      ...range,
      store_id: storeId.value,
    })
    if ((response.code === 0 || response.code === 200) && response.data) {
      if (hasCloseData(response.data)) {
        closeGeneratedAt.value = response.data.generated_at
        closePeriod.value = {
          start: response.data.period_start,
          end: response.data.period_end,
        }
        closeScore.value = response.data.close_score
        closeChecklist.value = response.data.checklist
        bankReconciliation.value = response.data.bank_reconciliation
        ledgerReadiness.value = response.data.ledger_readiness
        closeActionItems.value = response.data.action_items
      } else {
        applyCloseFallback()
      }
    } else {
      applyCloseFallback()
    }
  } catch {
    ElMessage.warning('关账准备接口暂不可用，已显示本地样例')
    applyCloseFallback()
  } finally {
    loading.value = false
  }
}

function applyFallback() {
  generatedAt.value = ''
  cards.value = [
    { key: 'cash_inflow', label: '经营现金流入', value: 2485630, unit: '元', tone: 'positive', description: '订单净额估算的经营现金流入。' },
    { key: 'cash_outflow', label: '经营现金流出', value: 1732120, unit: '元', tone: 'warning', description: '已审批/已支付费用估算的经营现金流出。' },
    { key: 'net_cash', label: '净现金流', value: 753510, unit: '元', tone: 'positive', description: '现金流入减现金流出。' },
    { key: 'budget_execution', label: '预算执行率', value: 86.2, unit: '%', tone: 'neutral', description: '查询期内可匹配预算科目的实际/预算。' },
    { key: 'open_receivable', label: '待确认营业款', value: 142300, unit: '元', tone: 'warning', description: '未完结订单对应的收入风险。' },
    { key: 'open_payable', label: '待付款费用', value: 218760, unit: '元', tone: 'warning', description: '已提交/已审批但未支付的费用压力。' },
  ]
  cashFlow.value = [
    { date: '2024-05-01', inflow: 76200, outflow: 45200, net: 31000, cumulative: 31000 },
    { date: '2024-05-06', inflow: 92800, outflow: 61000, net: 31800, cumulative: 62800 },
    { date: '2024-05-11', inflow: 84500, outflow: 73500, net: 11000, cumulative: 73800 },
    { date: '2024-05-16', inflow: 108600, outflow: 63200, net: 45400, cumulative: 119200 },
    { date: '2024-05-21', inflow: 99700, outflow: 81200, net: 18500, cumulative: 137700 },
    { date: '2024-05-26', inflow: 116200, outflow: 77400, net: 38800, cumulative: 176500 },
    { date: '2024-05-31', inflow: 124500, outflow: 86800, net: 37700, cumulative: 214200 },
  ]
  workingCapital.value = [
    { key: 'receivables', name: '应收/待确认营业款', amount: 142300, count: 23, risk_level: 'medium', suggestion: '跟进未完结订单，优先核对高金额堂食/外卖结算差异。' },
    { key: 'unsettled_orders', name: '未记录收款时间订单', amount: 68300, count: 16, risk_level: 'low', suggestion: '补齐支付流水时间，避免收入确认与银行对账脱节。' },
    { key: 'payables', name: '应付/待付款费用', amount: 218760, count: 31, risk_level: 'medium', suggestion: '按供应商和账期排款，避免审批后付款堆积。' },
  ]
  budgetControls.value = [
    { name: '人工成本', actual: 412360, budget: 390000, variance: 22360, execution_rate: 105.7, status: 'over' },
    { name: '能源费用', actual: 86730, budget: 92000, variance: -5270, execution_rate: 94.3, status: 'watch' },
    { name: '营销费用', actual: 65420, budget: 80000, variance: -14580, execution_rate: 81.8, status: 'normal' },
    { name: '租金及物业', actual: 138540, budget: 170000, variance: -31460, execution_rate: 81.5, status: 'normal' },
  ]
  capabilityMatrix.value = [
    { key: 'cash_flow', name: '现金流监控', category: '资金', status: 'ready', maturity_score: 82, current_support: '按订单实收与已审批/已支付费用生成日度现金流曲线。', next_actions: ['接入银行流水', '增加账户余额快照', '建立收付款核销关系'], evidence_metrics: ['营业现金流入', '经营现金流出'] },
    { key: 'working_capital', name: '应收应付与结算', category: '往来', status: 'partial', maturity_score: 68, current_support: '从未完结订单、未记录收款时间订单和待付款费用估算风险。', next_actions: ['补充客户/供应商账期', '建立发票与收付款状态', '按账龄输出清单'], evidence_metrics: ['待确认营业款', '待付款费用'] },
    { key: 'budget_control', name: '预算控制', category: '经营控制', status: 'ready', maturity_score: 78, current_support: '按费用科目对比预算、实际、差异和执行率。', next_actions: ['预算版本管理', '超预算审批流', '滚动预测'], evidence_metrics: ['预算执行率', '费用结构'] },
    { key: 'general_ledger', name: '总账与会计期间', category: '核算', status: 'planned', maturity_score: 35, current_support: '目前以经营分析口径聚合，还没有凭证、科目余额和关账流程。', next_actions: ['设计会计科目表', '建立凭证分录', '增加期间关账权限'], evidence_metrics: ['收入', '费用', '利润'] },
    { key: 'fixed_assets', name: '固定资产', category: '资产', status: 'planned', maturity_score: 28, current_support: '暂未区分设备、装修、摊销和折旧。', next_actions: ['建设资产卡片', '折旧规则', '盘点与处置流程'], evidence_metrics: ['门店面积', '费用记录'] },
    { key: 'tax_compliance', name: '税务与合规', category: '合规', status: 'planned', maturity_score: 30, current_support: '已有审计日志和基础报表，税率、发票勾稽和纳税申报尚未建模。', next_actions: ['增加发票台账', '维护税率规则', '生成税务辅助报表'], evidence_metrics: ['发票号', '审计日志'] },
  ]
  actionItems.value = [
    { priority: 'P1', title: '冻结或复核「人工成本」新增支出', owner: '预算负责人', reason: '执行率 105.7%，已超过预算控制线。', due_hint: '2 个工作日内' },
    { priority: 'P1', title: '处理应付/待付款费用', owner: '出纳/会计', reason: '未闭环金额 218760 元，影响资金预测准确性。', due_hint: '本周内' },
    { priority: 'P2', title: '补齐总账、资产和税务台账', owner: '财务信息化负责人', reason: '经营分析可用，下一阶段需要沉淀核算闭环。', due_hint: '本月规划会' },
  ]
}

function applyCloseFallback() {
  closeGeneratedAt.value = ''
  closePeriod.value = { start: '2024-05-01', end: '2024-05-31' }
  closeScore.value = 78
  closeChecklist.value = [
    {
      key: 'data_import_trace',
      name: '数据导入追溯',
      owner: '数据管理员',
      status: 'warning',
      ready_count: 4280,
      issue_count: 2,
      amount: 0,
      description: '最近两批费用导入存在部分失败，需要保留错误报告并补导。',
      next_step: '复核失败/部分失败批次并归档错误报告。',
    },
    {
      key: 'revenue_confirmation',
      name: '收入确认与收款时间',
      owner: '门店会计',
      status: 'blocker',
      ready_count: 18712,
      issue_count: 20,
      amount: 68300,
      description: '仍有未记录收款时间或未完结订单，会影响收入底稿。',
      next_step: '补齐收款时间，核对未完结订单是否应跨期或撤销。',
    },
    {
      key: 'expense_approval',
      name: '费用审批与发票完整性',
      owner: '费用会计',
      status: 'warning',
      ready_count: 646,
      issue_count: 17,
      amount: 86240,
      description: '部分费用处于待审批状态，发票号也需要继续补齐。',
      next_step: '先处理待审批费用，再按供应商补齐发票号和附件。',
    },
    {
      key: 'payment_cutoff',
      name: '付款截止与应付清单',
      owner: '出纳',
      status: 'warning',
      ready_count: 612,
      issue_count: 31,
      amount: 218760,
      description: '已审批未支付费用需要确认是否纳入本期应付。',
      next_step: '确认是否纳入本期应付，形成排款和银行付款清单。',
    },
    {
      key: 'budget_coverage',
      name: '预算覆盖与执行复核',
      owner: '预算负责人',
      status: 'ready',
      ready_count: 96,
      issue_count: 0,
      amount: 0,
      description: '本期预算记录可支持预算执行复核。',
      next_step: '标记超预算科目并同步预算责任人。',
    },
    {
      key: 'audit_trail',
      name: '审计留痕',
      owner: '系统管理员',
      status: 'ready',
      ready_count: 605,
      issue_count: 0,
      amount: 0,
      description: '查询、导入、导出和关键变更均有审计日志。',
      next_step: '保留审计日志作为关账附件。',
    },
  ]
  bankReconciliation.value = [
    { channel: '收款-wechat', direction: 'inflow', expected_amount: 1086320, record_count: 8220, unmatched_count: 7, unmatched_amount: 21450, status: 'warning', account_hint: '以支付方式映射微信商户收款账户。' },
    { channel: '收款-alipay', direction: 'inflow', expected_amount: 842610, record_count: 6410, unmatched_count: 5, unmatched_amount: 16880, status: 'warning', account_hint: '以支付方式映射支付宝商户收款账户。' },
    { channel: '付款-bank', direction: 'outflow', expected_amount: 318760, record_count: 88, unmatched_count: 12, unmatched_amount: 92800, status: 'blocker', account_hint: '核对支付账户、付款状态与银行付款流水。' },
    { channel: '付款-cash', direction: 'outflow', expected_amount: 48500, record_count: 26, unmatched_count: 0, unmatched_amount: 0, status: 'ready', account_hint: '现金备用金台账已能匹配。' },
  ]
  ledgerReadiness.value = [
    { key: 'revenue_workpaper', name: '收入凭证底稿', status: 'blocker', coverage: 91, source: 'order_header', remark: '以订单净额、业务日期、支付方式和收款时间生成收入底稿。' },
    { key: 'expense_workpaper', name: '费用凭证底稿', status: 'warning', coverage: 88, source: 'expense_record', remark: '以费用科目、供应商、发票号、审批状态和付款状态生成费用底稿。' },
    { key: 'budget_workpaper', name: '预算执行底稿', status: 'ready', coverage: 100, source: 'budgets', remark: '预算记录可支持本期实际、预算、差异和执行率复核。' },
    { key: 'audit_workpaper', name: '审计追溯底稿', status: 'ready', coverage: 100, source: 'audit_log', remark: '审计日志用于追溯导入、查询、导出和关键变更。' },
    { key: 'general_ledger_model', name: '总账模型', status: 'planned', coverage: 35, source: 'planned', remark: '下一步需要会计科目表、凭证分录、期间关账和反关账权限。' },
  ]
  closeActionItems.value = [
    { priority: 'P0', title: '处理收入确认与收款时间差异', owner: '门店会计', reason: '仍有 20 笔订单影响收入底稿，金额 68300 元。', due_hint: '关账前' },
    { priority: 'P1', title: '确认已审批未付款费用是否转应付', owner: '出纳', reason: '已审批未支付 31 笔，金额 218760 元。', due_hint: '关账检查会前' },
    { priority: 'P2', title: '进入总账与期间关账建模', owner: '财务信息化负责人', reason: '现有经营数据已能支撑关账前检查，下一阶段可设计科目、凭证和期间状态。', due_hint: '下阶段迭代' },
  ]
}

function renderCashFlow() {
  const option: ECOption = {
    legend: {
      top: 10,
      right: 16,
      textStyle: { color: MUTED, fontSize: 12 },
    },
    grid: { left: 42, right: 24, top: 52, bottom: 34 },
    xAxis: {
      type: 'category',
      data: cashFlow.value.map(item => dayjs(item.date).format('MM-DD')),
      axisLine: { lineStyle: { color: '#D7CEC2' } },
      axisTick: { show: false },
      axisLabel: { color: MUTED },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: MUTED,
        formatter: (value: number) => `${Math.round(value / 10000)}万`,
      },
      splitLine: { lineStyle: { color: '#EEE7DC', type: 'dashed' } },
    },
    tooltip: {
      trigger: 'axis',
      valueFormatter: (value: unknown) => {
        const raw = Array.isArray(value) ? value[0] : value
        const numeric = Number(raw || 0)
        return money(Number.isFinite(numeric) ? numeric : 0)
      },
    },
    series: [
      {
        name: '流入',
        type: 'line',
        data: cashFlow.value.map(item => item.inflow),
        itemStyle: { color: GREEN },
      },
      {
        name: '流出',
        type: 'line',
        data: cashFlow.value.map(item => item.outflow),
        itemStyle: { color: GOLD },
      },
      {
        name: '累计净现金流',
        type: 'line',
        data: cashFlow.value.map(item => item.cumulative),
        itemStyle: { color: RED },
      },
    ],
  }
  setCashFlowOption(option, true)
}

function formatMetric(value: number, unit: string) {
  if (unit === '%') return `${value.toFixed(1)}%`
  if (unit === '元') return money(value)
  return `${value.toLocaleString('zh-CN')} ${unit}`.trim()
}

function money(value: number) {
  return `¥ ${Number(value || 0).toLocaleString('zh-CN', { maximumFractionDigits: 0 })}`
}

function cardIcon(key: string): Component {
  const iconMap: Record<string, Component> = {
    cash_inflow: markRaw(Money),
    cash_outflow: markRaw(Wallet),
    net_cash: markRaw(TrendCharts),
    budget_execution: markRaw(Tickets),
    open_receivable: markRaw(Clock),
    open_payable: markRaw(Warning),
  }
  return iconMap[key] || markRaw(Money)
}

function riskTag(level: string) {
  if (level === 'high') return 'danger'
  if (level === 'medium') return 'warning'
  return 'success'
}

function riskLabel(level: string) {
  if (level === 'high') return '高'
  if (level === 'medium') return '中'
  return '低'
}

function budgetTag(status: string) {
  if (status === 'over') return 'danger'
  if (status === 'watch') return 'warning'
  return 'success'
}

function budgetLabel(status: string) {
  if (status === 'over') return '超支'
  if (status === 'watch') return '关注'
  return '正常'
}

function capabilityTag(status: string) {
  if (status === 'ready') return 'success'
  if (status === 'partial') return 'warning'
  return 'info'
}

function capabilityLabel(status: string) {
  if (status === 'ready') return '已落地'
  if (status === 'partial') return '部分支持'
  return '规划中'
}

function progressColor(status: string) {
  if (status === 'ready') return GREEN
  if (status === 'partial') return GOLD
  return '#7A8289'
}

function closeStatusTag(status: string) {
  if (status === 'blocker') return 'danger'
  if (status === 'warning') return 'warning'
  if (status === 'ready') return 'success'
  return 'info'
}

function closeStatusLabel(status: string) {
  if (status === 'blocker') return '阻断'
  if (status === 'warning') return '关注'
  if (status === 'ready') return '就绪'
  if (status === 'planned') return '规划中'
  return status
}

function closeProgressColor(status: string) {
  if (status === 'blocker') return RED
  if (status === 'warning') return GOLD
  if (status === 'ready') return GREEN
  return '#7A8289'
}

function directionLabel(direction: string) {
  return direction === 'inflow' ? '流入' : '流出'
}

function priorityClass(priority: string) {
  return {
    p0: priority === 'P0',
    p1: priority === 'P1',
    p2: priority === 'P2',
  }
}

onMounted(async () => {
  applyFallback()
  applyCloseFallback()
  await nextTick()
  renderCashFlow()
  fetchActiveView()
})
</script>

<style scoped lang="scss">
.finance-center-page {
  display: grid;
  gap: 12px;
}

.finance-center-toolbar {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;

  h1 {
    margin: 2px 0 0;
    color: #211A15;
    font-size: 23px;
    font-weight: 900;
  }
}

.eyebrow {
  margin: 0;
  color: #8A8074;
  font-size: 12px;
  font-weight: 900;
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

.freshness-line {
  display: flex;
  justify-content: flex-end;
  gap: 18px;
  color: #8A8074;
  font-size: 12px;
  font-weight: 700;
}

.finance-card-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 10px;
}

.finance-card,
.panel {
  background: rgba(255, 253, 249, 0.96);
  border: 1px solid #E5DED4;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
}

.finance-card {
  min-height: 154px;
  padding: 15px 14px;
  position: relative;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    inset: auto 0 0;
    height: 3px;
    background: #D7CEC2;
  }

  &.positive::after {
    background: #2F8F5B;
  }

  &.warning::after {
    background: #D19A36;
  }

  &.danger::after {
    background: #C81E1E;
  }

  strong {
    display: block;
    margin-top: 15px;
    color: #17110D;
    font-size: 25px;
    font-weight: 900;
    line-height: 1;
    white-space: nowrap;
  }

  p {
    margin: 14px 0 0;
    color: #756D64;
    font-size: 12px;
    line-height: 1.45;
  }
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  color: #332D28;
  font-size: 14px;
  font-weight: 900;

  .el-icon {
    color: #C81E1E;
    font-size: 20px;
  }
}

.finance-main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.42fr) minmax(330px, 0.72fr);
  gap: 10px;
}

.finance-lower-grid {
  display: grid;
  grid-template-columns: minmax(300px, 0.78fr) minmax(330px, 0.9fr) minmax(380px, 1.18fr);
  gap: 10px;
}

.close-score-band {
  display: grid;
  grid-template-columns: minmax(320px, 1.3fr) repeat(3, minmax(180px, 0.72fr));
  gap: 10px;
}

.score-panel {
  display: grid;
  grid-template-columns: 138px minmax(0, 1fr);
  align-items: center;
  gap: 12px;

  div {
    display: grid;
    gap: 3px;
  }

  span {
    color: #756D64;
    font-size: 12px;
    font-weight: 900;
  }

  strong {
    color: #17110D;
    font-size: 42px;
    line-height: 0.95;
  }

  p {
    grid-column: 1 / -1;
    margin: 0;
    color: #8A8074;
    font-size: 12px;
    font-weight: 800;
  }
}

.close-stat {
  display: grid;
  gap: 8px;
  min-height: 112px;

  span {
    color: #756D64;
    font-size: 12px;
    font-weight: 900;
  }

  strong {
    color: #17110D;
    font-size: 28px;
    line-height: 1;
  }

  p {
    margin: 0;
    color: #8A8074;
    font-size: 12px;
    line-height: 1.45;
  }
}

.close-check-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.close-check-card {
  position: relative;
  display: grid;
  gap: 10px;
  min-height: 174px;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0 auto 0 0;
    width: 4px;
    background: #D7CEC2;
  }

  &.ready::before {
    background: #2F8F5B;
  }

  &.warning::before {
    background: #D19A36;
  }

  &.blocker::before {
    background: #C81E1E;
  }

  p {
    margin: 0;
    color: #554D46;
    font-size: 12px;
    line-height: 1.5;
  }

  small {
    color: #8A8074;
    font-size: 12px;
    font-weight: 800;
    line-height: 1.45;
  }
}

.close-check-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;

  div {
    display: grid;
    gap: 3px;
  }

  strong {
    color: #211A15;
    font-size: 15px;
    font-weight: 900;
  }

  span {
    color: #8A8074;
    font-size: 12px;
    font-weight: 800;
  }
}

.close-check-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;

  span {
    padding: 7px 8px;
    background: #FAF8F4;
    border: 1px solid #EEE7DC;
    border-radius: 5px;
    color: #554D46;
    font-size: 12px;
    font-weight: 900;
    text-align: center;
    white-space: nowrap;
  }
}

.close-main-grid {
  display: grid;
  grid-template-columns: minmax(440px, 1.16fr) minmax(360px, 0.92fr) minmax(320px, 0.78fr);
  gap: 10px;
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

.cashflow-chart {
  width: 100%;
  height: 326px;
}

.action-list {
  display: grid;
  gap: 10px;
  padding-top: 12px;
}

.action-item {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 10px;
  padding: 12px;
  background: #FAF8F4;
  border: 1px solid #EEE7DC;
  border-radius: 6px;

  > b {
    display: grid;
    place-items: center;
    height: 32px;
    border-radius: 6px;
    color: #fff;
    font-size: 12px;

    &.p0 {
      background: #C81E1E;
    }

    &.p1 {
      background: #D19A36;
    }

    &.p2 {
      background: #657078;
    }
  }

  strong {
    color: #211A15;
    font-size: 13px;
  }

  p {
    margin: 5px 0;
    color: #554D46;
    font-size: 12px;
    line-height: 1.5;
  }

  span {
    color: #8A8074;
    font-size: 12px;
    font-weight: 700;
  }
}

.capital-list,
.capability-list {
  display: grid;
  gap: 10px;
  padding-top: 12px;
}

.capital-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 10px;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #F0E9DF;

  &:last-child {
    border-bottom: 0;
  }

  div {
    display: grid;
    gap: 3px;
  }

  strong {
    color: #211A15;
    font-size: 13px;
    font-weight: 900;
  }

  span {
    color: #8A8074;
    font-size: 12px;
  }

  > b {
    color: #17110D;
    font-size: 16px;
    white-space: nowrap;
  }

  p {
    grid-column: 1 / -1;
    margin: 0;
    color: #756D64;
    font-size: 12px;
    line-height: 1.45;
  }
}

.finance-table {
  width: 100%;
  margin-top: 12px;
  border-collapse: collapse;
  color: #554D46;
  font-size: 12px;

  th,
  td {
    padding: 10px 8px;
    border-bottom: 1px solid #F0E9DF;
    text-align: right;
    white-space: nowrap;
  }

  th {
    color: #8A8074;
    font-weight: 900;
  }

  th:first-child,
  td:first-child {
    text-align: left;
  }

  .table-empty {
    color: #8A8074;
    font-weight: 800;
    text-align: center;
  }
}

.close-bank-table {
  td:first-child {
    strong {
      display: block;
      color: #211A15;
      font-size: 12px;
      font-weight: 900;
    }

    span {
      display: block;
      margin-top: 3px;
      color: #8A8074;
      font-size: 11px;
      font-weight: 700;
      white-space: normal;
    }
  }
}

.capability-item {
  padding: 12px;
  background: #FAF8F4;
  border: 1px solid #EEE7DC;
  border-radius: 6px;

  p {
    margin: 9px 0;
    color: #554D46;
    font-size: 12px;
    line-height: 1.5;
  }
}

.ledger-list {
  display: grid;
  gap: 10px;
  padding-top: 12px;
}

.ledger-item {
  display: grid;
  grid-template-columns: minmax(130px, 0.74fr) minmax(120px, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 11px 0;
  border-bottom: 1px solid #F0E9DF;

  &:last-child {
    border-bottom: 0;
  }

  div {
    display: grid;
    gap: 3px;
  }

  strong {
    color: #211A15;
    font-size: 13px;
    font-weight: 900;
  }

  span {
    color: #8A8074;
    font-size: 11px;
    font-weight: 800;
  }

  p {
    grid-column: 1 / -1;
    margin: 0;
    color: #756D64;
    font-size: 12px;
    line-height: 1.45;
  }
}

.capability-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;

  div {
    display: grid;
    gap: 3px;
  }

  strong {
    color: #211A15;
    font-size: 14px;
    font-weight: 900;
  }

  span {
    color: #8A8074;
    font-size: 12px;
  }
}

.next-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;

  span {
    padding: 4px 7px;
    border-radius: 5px;
    background: #FFFDF9;
    color: #756D64;
    font-size: 11px;
    font-weight: 800;
  }
}

@media (max-width: 1380px) {
  .finance-card-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .finance-main-grid,
  .finance-lower-grid,
  .close-score-band,
  .close-check-grid,
  .close-main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .finance-center-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .toolbar-controls {
    justify-content: flex-start;
  }

  .freshness-line {
    justify-content: flex-start;
    flex-direction: column;
    gap: 4px;
  }

  .finance-card-grid {
    grid-template-columns: 1fr;
  }

  .score-panel,
  .ledger-item,
  .close-check-metrics {
    grid-template-columns: 1fr;
  }

  .finance-table {
    display: block;
    overflow-x: auto;
  }
}
</style>
