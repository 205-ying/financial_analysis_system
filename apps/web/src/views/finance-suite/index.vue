<template>
  <div class="finance-suite-page">
    <section class="suite-toolbar">
      <div>
        <p class="eyebrow">Finance Accounting Suite</p>
        <h1>财务核算中心</h1>
      </div>

      <div class="toolbar-controls">
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
        <el-button type="primary" :icon="Search" :loading="loading" @click="fetchSuite">
          查询
        </el-button>
        <el-tooltip content="刷新财务核算中心" placement="top">
          <el-button :icon="RefreshRight" circle :loading="loading" @click="fetchSuite" />
        </el-tooltip>
      </div>
    </section>

    <div class="freshness-line">
      <span>数据生成：{{ generatedAtLabel }}</span>
      <span>期间：{{ periodLabel }}</span>
      <span>口径：经营数据预核算、对账准备、税票测算、关账合并预览</span>
    </div>

    <section class="suite-kpi-band">
      <article v-for="item in suiteStats" :key="item.label" class="suite-stat">
        <span>{{ item.label }}</span>
        <strong class="font-number">{{ item.value }}</strong>
        <p>{{ item.hint }}</p>
      </article>
    </section>

    <section class="suite-module-grid">
      <button
        v-for="module in modules"
        :key="module.key"
        :class="['module-card', module.status, { active: selectedModule === module.key }]"
        type="button"
        @click="selectedModule = module.key"
      >
        <div class="module-top">
          <b>{{ module.priority }}</b>
          <el-icon><component :is="moduleIcon(module.key)" /></el-icon>
        </div>
        <strong>{{ module.name }}</strong>
        <span>{{ module.metric_label }}</span>
        <em class="font-number">{{ formatModuleMetric(module.metric_value) }}</em>
        <p>{{ module.description }}</p>
        <div class="module-foot">
          <el-progress
            :percentage="module.maturity_score"
            :stroke-width="7"
            :color="statusColor(module.status)"
          />
          <small>{{ statusLabel(module.status) }} · {{ module.issue_count }} 项</small>
        </div>
      </button>
    </section>

    <section class="suite-workbench">
      <article class="panel detail-panel">
        <header class="panel-header">
          <div>
            <h2>{{ activeModule?.name || '模块明细' }}</h2>
            <span>{{ activeModule?.description || '暂无模块说明' }}</span>
          </div>
          <el-tag :type="statusTag(activeModule?.status || 'planned')" effect="plain">
            {{ statusLabel(activeModule?.status || 'planned') }}
          </el-tag>
        </header>

        <template v-if="selectedModule === 'general_ledger'">
          <div class="ledger-period-list">
            <div v-for="item in generalLedgerPeriods" :key="item.period" class="period-row">
              <strong>{{ item.period }}</strong>
              <span>收入 {{ money(item.revenue_amount) }}</span>
              <span>费用 {{ money(item.expense_amount) }}</span>
              <span>未过账 {{ item.unposted_count }}</span>
              <el-tag :type="statusTag(item.status)" effect="plain">{{ statusLabel(item.status) }}</el-tag>
              <p>{{ item.next_step }}</p>
            </div>
          </div>
          <h3>科目映射</h3>
          <table class="suite-table">
            <thead>
              <tr>
                <th>编码</th>
                <th>科目</th>
                <th>类别</th>
                <th>方向</th>
                <th>来源</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in chartOfAccounts" :key="item.code">
                <td>{{ item.code }}</td>
                <td>{{ item.name }}</td>
                <td>{{ accountCategoryLabel(item.category) }}</td>
                <td>{{ directionText(item.balance_direction) }}</td>
                <td>{{ item.mapped_source }}</td>
                <td><el-tag :type="statusTag(item.status)" effect="plain">{{ statusLabel(item.status) }}</el-tag></td>
              </tr>
            </tbody>
          </table>
          <h3>凭证预览</h3>
          <table class="suite-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>摘要</th>
                <th>借方</th>
                <th>贷方</th>
                <th>金额</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in journalEntryPreviews" :key="`${item.source_type}-${item.summary}`">
                <td>{{ item.entry_date }}</td>
                <td>{{ item.summary }}</td>
                <td>{{ item.debit_account }}</td>
                <td>{{ item.credit_account }}</td>
                <td>{{ money(item.amount) }}</td>
                <td><el-tag :type="statusTag(item.status)" effect="plain">{{ statusLabel(item.status) }}</el-tag></td>
              </tr>
            </tbody>
          </table>
        </template>

        <template v-else-if="selectedModule === 'bank_reconciliation'">
          <table class="suite-table">
            <thead>
              <tr>
                <th>账户/通道</th>
                <th>方向</th>
                <th>应对账</th>
                <th>已匹配</th>
                <th>未匹配</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!bankAccounts.length">
                <td class="table-empty" colspan="6">暂无可对账收付款通道</td>
              </tr>
              <tr v-for="item in bankAccounts" :key="`${item.direction}-${item.name}`">
                <td>{{ item.name }}</td>
                <td>{{ flowDirectionLabel(item.direction) }}</td>
                <td>{{ money(item.statement_amount) }}</td>
                <td>{{ money(item.matched_amount) }}</td>
                <td>{{ item.unmatched_count }} / {{ money(item.unmatched_amount) }}</td>
                <td><el-tag :type="statusTag(item.status)" effect="plain">{{ statusLabel(item.status) }}</el-tag></td>
              </tr>
            </tbody>
          </table>
        </template>

        <template v-else-if="selectedModule === 'receivable_payable'">
          <table class="suite-table">
            <thead>
              <tr>
                <th>往来对象</th>
                <th>类型</th>
                <th>金额</th>
                <th>记录数</th>
                <th>账龄</th>
                <th>动作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="!counterpartyLedgers.length">
                <td class="table-empty" colspan="6">暂无未结往来款</td>
              </tr>
              <tr v-for="item in counterpartyLedgers" :key="`${item.ledger_type}-${item.counterparty}`">
                <td>{{ item.counterparty }}</td>
                <td>{{ ledgerTypeLabel(item.ledger_type) }}</td>
                <td>{{ money(item.amount) }}</td>
                <td>{{ item.record_count }}</td>
                <td><el-tag :type="statusTag(item.status)" effect="plain">{{ item.aging_bucket }}</el-tag></td>
                <td>{{ item.next_step }}</td>
              </tr>
            </tbody>
          </table>
        </template>

        <template v-else-if="selectedModule === 'budget_workflow'">
          <table class="suite-table">
            <thead>
              <tr>
                <th>版本</th>
                <th>范围</th>
                <th>预算</th>
                <th>实际</th>
                <th>差异</th>
                <th>审批</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in budgetVersions" :key="`${item.version_name}-${item.scope}`">
                <td>{{ item.version_name }}</td>
                <td>{{ item.scope }}</td>
                <td>{{ money(item.budget_amount) }}</td>
                <td>{{ money(item.actual_amount) }}</td>
                <td>{{ money(item.variance_amount) }}</td>
                <td><el-tag :type="approvalTag(item.approval_status)" effect="plain">{{ approvalLabel(item.approval_status) }}</el-tag></td>
              </tr>
            </tbody>
          </table>
        </template>

        <template v-else-if="selectedModule === 'fixed_assets'">
          <table class="suite-table">
            <thead>
              <tr>
                <th>资产</th>
                <th>门店</th>
                <th>类别</th>
                <th>原值</th>
                <th>月折旧</th>
                <th>净值</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in fixedAssets" :key="`${item.store_name}-${item.asset_name}`">
                <td>{{ item.asset_name }}</td>
                <td>{{ item.store_name }}</td>
                <td>{{ item.category }}</td>
                <td>{{ money(item.original_value) }}</td>
                <td>{{ money(item.monthly_depreciation) }}</td>
                <td>{{ money(item.net_value) }}</td>
                <td><el-tag :type="statusTag(item.status)" effect="plain">{{ statusLabel(item.status) }}</el-tag></td>
              </tr>
            </tbody>
          </table>
        </template>

        <template v-else-if="selectedModule === 'tax_invoice'">
          <table class="suite-table">
            <thead>
              <tr>
                <th>票据类型</th>
                <th>来源</th>
                <th>含税基础</th>
                <th>税率</th>
                <th>税额</th>
                <th>发票/缺票</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in taxInvoices" :key="`${item.invoice_type}-${item.source}`">
                <td>{{ invoiceTypeLabel(item.invoice_type) }}</td>
                <td>{{ item.source }}</td>
                <td>{{ money(item.taxable_amount) }}</td>
                <td>{{ item.tax_rate.toFixed(1) }}%</td>
                <td>{{ money(item.tax_amount) }}</td>
                <td>{{ item.invoice_count }} / {{ item.missing_invoice_count }}</td>
                <td><el-tag :type="statusTag(item.status)" effect="plain">{{ statusLabel(item.status) }}</el-tag></td>
              </tr>
            </tbody>
          </table>
        </template>

        <template v-else>
          <table class="suite-table">
            <thead>
              <tr>
                <th>合并范围</th>
                <th>收入</th>
                <th>费用</th>
                <th>利润</th>
                <th>阻断项</th>
                <th>状态</th>
                <th>说明</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in closeConsolidation" :key="item.store_name">
                <td>{{ item.store_name }}</td>
                <td>{{ money(item.revenue_amount) }}</td>
                <td>{{ money(item.expense_amount) }}</td>
                <td>{{ money(item.profit_amount) }}</td>
                <td>{{ item.blocker_count }}</td>
                <td><el-tag :type="statusTag(item.close_status)" effect="plain">{{ statusLabel(item.close_status) }}</el-tag></td>
                <td>{{ item.consolidation_note }}</td>
              </tr>
            </tbody>
          </table>
        </template>
      </article>

      <aside class="panel action-panel">
        <header class="panel-header compact">
          <div>
            <h2>闭环行动</h2>
            <span>按阻断程度生成</span>
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
      </aside>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, markRaw, onMounted, ref, type Component } from 'vue'
import dayjs from 'dayjs'
import {
  Connection,
  Document,
  Finished,
  Money,
  RefreshRight,
  Search,
  SetUp,
  Tickets,
  TrendCharts,
  Wallet,
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import StoreSelect from '@/components/StoreSelect.vue'
import { getFinanceSuiteOverview } from '@/api/finance'
import { DEMO_PERIOD } from '@/config'
import type {
  BankAccountItem,
  BudgetVersionItem,
  ChartOfAccountItem,
  CloseConsolidationItem,
  CounterpartyLedgerItem,
  FinanceActionItem,
  FinanceSuiteModule,
  FinanceSuiteOverview,
  FixedAssetItem,
  GeneralLedgerPeriodItem,
  JournalEntryPreviewItem,
  TaxInvoiceItem,
} from '@/types'

type QuickRange = 'demo' | 'month' | 'last_month' | 'quarter' | 'custom'

const RED = '#C81E1E'
const GREEN = '#2F8F5B'
const GOLD = '#D19A36'

const storeId = ref<number | undefined>(undefined)
const quickRange = ref<QuickRange>('demo')
const customDateRange = ref<[string, string]>()
const loading = ref(false)
const generatedAt = ref('')
const period = ref({ start: '', end: '' })
const selectedModule = ref('general_ledger')

const modules = ref<FinanceSuiteModule[]>([])
const generalLedgerPeriods = ref<GeneralLedgerPeriodItem[]>([])
const chartOfAccounts = ref<ChartOfAccountItem[]>([])
const journalEntryPreviews = ref<JournalEntryPreviewItem[]>([])
const bankAccounts = ref<BankAccountItem[]>([])
const counterpartyLedgers = ref<CounterpartyLedgerItem[]>([])
const budgetVersions = ref<BudgetVersionItem[]>([])
const fixedAssets = ref<FixedAssetItem[]>([])
const taxInvoices = ref<TaxInvoiceItem[]>([])
const closeConsolidation = ref<CloseConsolidationItem[]>([])
const actionItems = ref<FinanceActionItem[]>([])

const generatedAtLabel = computed(() => {
  return generatedAt.value ? dayjs(generatedAt.value).format('YYYY-MM-DD HH:mm') : '本地样例'
})

const periodLabel = computed(() => {
  const range = getDateRange()
  return `${period.value.start || range.start_date} ~ ${period.value.end || range.end_date}`
})

const activeModule = computed(() => {
  return modules.value.find(item => item.key === selectedModule.value)
})

const suiteStats = computed(() => {
  const issueCount = modules.value.reduce((sum, item) => sum + item.issue_count, 0)
  const maturity = modules.value.length
    ? Math.round(modules.value.reduce((sum, item) => sum + item.maturity_score, 0) / modules.value.length)
    : 0
  const highPriority = modules.value.filter(item => item.priority === 'P0' && item.issue_count > 0).length
  return [
    { label: '剩余模块', value: modules.value.length, hint: '总账、银行、往来、预算、资产、税票、合并' },
    { label: '平均成熟度', value: `${maturity}%`, hint: '按当前经营数据支撑度估算' },
    { label: '待处理项', value: issueCount, hint: `${highPriority} 个 P0 模块存在待清理项` },
    { label: '行动数', value: actionItems.value.length, hint: '从阻断项自动生成优先动作' },
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

function hasSuiteData(data: FinanceSuiteOverview) {
  const hasModuleMetric = (data.modules || []).some(item => Math.abs(Number(item.metric_value || 0)) > 0 || Number(item.issue_count || 0) > 0)
  const hasLedger = (data.general_ledger_periods || []).some(item =>
    Math.abs(Number(item.revenue_amount || 0)) + Math.abs(Number(item.expense_amount || 0)) + Number(item.unposted_count || 0) > 0
  )
  const hasBank = (data.bank_accounts || []).some(item => Math.abs(Number(item.statement_amount || 0)) + Math.abs(Number(item.unmatched_amount || 0)) > 0)
  const hasCounterparty = (data.counterparty_ledgers || []).some(item => Math.abs(Number(item.amount || 0)) > 0)
  const hasTax = (data.tax_invoices || []).some(item => Math.abs(Number(item.taxable_amount || 0)) + Number(item.missing_invoice_count || 0) > 0)
  return hasModuleMetric || hasLedger || hasBank || hasCounterparty || hasTax
}

function handleQuickRangeChange() {
  if (quickRange.value !== 'custom') {
    fetchSuite()
  }
}

async function fetchSuite() {
  const range = getDateRange()
  loading.value = true
  try {
    const response = await getFinanceSuiteOverview({
      ...range,
      store_id: storeId.value,
    })
    if ((response.code === 0 || response.code === 200) && response.data) {
      if (hasSuiteData(response.data)) {
        generatedAt.value = response.data.generated_at
        period.value = {
          start: response.data.period_start,
          end: response.data.period_end,
        }
        modules.value = response.data.modules
        generalLedgerPeriods.value = response.data.general_ledger_periods
        chartOfAccounts.value = response.data.chart_of_accounts
        journalEntryPreviews.value = response.data.journal_entry_previews
        bankAccounts.value = response.data.bank_accounts
        counterpartyLedgers.value = response.data.counterparty_ledgers
        budgetVersions.value = response.data.budget_versions
        fixedAssets.value = response.data.fixed_assets
        taxInvoices.value = response.data.tax_invoices
        closeConsolidation.value = response.data.close_consolidation
        actionItems.value = response.data.action_items
        if (!modules.value.some(item => item.key === selectedModule.value)) {
          selectedModule.value = modules.value[0]?.key || 'general_ledger'
        }
      } else {
        applyFallback()
      }
    } else {
      applyFallback()
    }
  } catch {
    ElMessage.warning('财务核算中心接口暂不可用，已显示本地样例')
    applyFallback()
  } finally {
    loading.value = false
  }
}

function applyFallback() {
  generatedAt.value = ''
  period.value = { start: '2024-05-01', end: '2024-05-31' }
  modules.value = [
    { key: 'general_ledger', name: '总账与会计期间', priority: 'P0', status: 'partial', maturity_score: 58, metric_label: '凭证预览金额', metric_value: 4217320, issue_count: 18, description: '科目映射和凭证预览已可用，正式过账需补期间锁定。' },
    { key: 'bank_reconciliation', name: '银行流水与对账', priority: 'P0', status: 'warning', maturity_score: 63, metric_label: '未匹配金额', metric_value: 154800, issue_count: 12, description: '收付款通道已识别，待接入真实银行流水。' },
    { key: 'receivable_payable', name: '应收应付台账', priority: 'P1', status: 'warning', maturity_score: 66, metric_label: '往来未结金额', metric_value: 361060, issue_count: 6, description: '从未完结订单和待付款费用生成往来台账。' },
    { key: 'budget_workflow', name: '预算版本与超预算审批', priority: 'P1', status: 'partial', maturity_score: 70, metric_label: '待审批版本', metric_value: 2, issue_count: 2, description: '滚动预算版本和审批需求已识别。' },
    { key: 'fixed_assets', name: '固定资产', priority: 'P1', status: 'partial', maturity_score: 56, metric_label: '资产净值', metric_value: 286300, issue_count: 3, description: '从资产类费用提取资产卡片线索并测算折旧。' },
    { key: 'tax_invoice', name: '税务与发票', priority: 'P2', status: 'warning', maturity_score: 60, metric_label: '缺票记录', metric_value: 17, issue_count: 17, description: '销项/进项税额测算和发票完整性检查已建立。' },
    { key: 'close_consolidation', name: '财务关账与合并', priority: 'P2', status: 'partial', maturity_score: 62, metric_label: '合并阻断项', metric_value: 18, issue_count: 18, description: '多门店合并预览可用，正式抵消分录待建模。' },
  ]
  generalLedgerPeriods.value = [{ period: '2024-05', status: 'checking', revenue_amount: 2485630, expense_amount: 1732120, journal_preview_count: 4, unposted_count: 18, next_step: '处理阻断项后生成正式凭证与期间锁定记录。' }]
  chartOfAccounts.value = [
    { code: '1002', name: '银行存款', category: 'asset', balance_direction: 'debit', mapped_source: '支付方式/支付账户', status: 'partial' },
    { code: '1122', name: '应收账款', category: 'asset', balance_direction: 'debit', mapped_source: '未完结订单', status: 'partial' },
    { code: '2202', name: '应付账款', category: 'liability', balance_direction: 'credit', mapped_source: '待付款费用', status: 'partial' },
    { code: '5001', name: '主营业务收入', category: 'revenue', balance_direction: 'credit', mapped_source: '订单净额', status: 'ready' },
    { code: '6601', name: '销售费用', category: 'expense', balance_direction: 'debit', mapped_source: '费用科目', status: 'ready' },
  ]
  journalEntryPreviews.value = [
    { source_type: 'orders', entry_date: '2024-05-31', summary: '营业收入确认', debit_account: '1002/1122', credit_account: '5001', amount: 2485630, status: 'blocked' },
    { source_type: 'expenses', entry_date: '2024-05-31', summary: '经营费用归集', debit_account: '6601', credit_account: '1002/2202', amount: 1732120, status: 'ready' },
  ]
  bankAccounts.value = [
    { name: '收款-wechat', channel: 'wechat', direction: 'inflow', statement_amount: 1086320, matched_amount: 1064870, unmatched_amount: 21450, unmatched_count: 7, status: 'warning' },
    { name: '付款-bank', channel: 'bank', direction: 'outflow', statement_amount: 318760, matched_amount: 225960, unmatched_amount: 92800, unmatched_count: 12, status: 'blocker' },
  ]
  counterpartyLedgers.value = [
    { counterparty: '销售渠道-delivery', ledger_type: 'receivable', amount: 142300, record_count: 23, aging_bucket: '0-30天', status: 'watch', next_step: '核对平台收款流水并完成收入核销。' },
    { counterparty: '未维护供应商', ledger_type: 'payable', amount: 218760, record_count: 31, aging_bucket: '本期待付款', status: 'watch', next_step: '确认付款计划、发票状态和应付入账期间。' },
  ]
  budgetVersions.value = [
    { version_name: '2024-05滚动预算', scope: '人工成本', budget_amount: 390000, actual_amount: 412360, variance_amount: 22360, approval_status: 'required', owner: '预算负责人' },
    { version_name: '2024-05滚动预算', scope: '能源费用', budget_amount: 92000, actual_amount: 86730, variance_amount: -5270, approval_status: 'pending', owner: '预算负责人' },
  ]
  fixedAssets.value = [
    { asset_name: '望京旗舰店-设备资产包', store_name: '望京旗舰店', category: '设备', original_value: 318000, monthly_depreciation: 8833, net_value: 309167, status: 'checking' },
  ]
  taxInvoices.value = [
    { invoice_type: 'output', source: '订单收入销项税测算', taxable_amount: 2485630, tax_rate: 6, tax_amount: 149138, invoice_count: 18732, missing_invoice_count: 0, status: 'ready' },
    { invoice_type: 'input', source: '费用进项票据台账', taxable_amount: 1732120, tax_rate: 6, tax_amount: 103927, invoice_count: 646, missing_invoice_count: 17, status: 'warning' },
  ]
  closeConsolidation.value = [
    { store_name: '合并口径', revenue_amount: 2485630, expense_amount: 1732120, profit_amount: 753510, close_status: 'checking', blocker_count: 18, consolidation_note: '多门店合并预览，暂不生成正式合并抵消分录。' },
  ]
  actionItems.value = [
    { priority: 'P0', title: '推进总账与会计期间问题清理', owner: '财务负责人', reason: '仍有 18 个待处理项，影响模块成熟度。', due_hint: '本期关账前' },
    { priority: 'P0', title: '推进银行流水与对账问题清理', owner: '财务负责人', reason: '仍有 12 个待处理项，影响模块成熟度。', due_hint: '本期关账前' },
  ]
}

function money(value: number) {
  return `¥ ${Number(value || 0).toLocaleString('zh-CN', { maximumFractionDigits: 0 })}`
}

function formatModuleMetric(value: number) {
  if (Math.abs(value) >= 10000) return money(value)
  return Number(value || 0).toLocaleString('zh-CN')
}

function moduleIcon(key: string): Component {
  const iconMap: Record<string, Component> = {
    general_ledger: markRaw(Document),
    bank_reconciliation: markRaw(Wallet),
    receivable_payable: markRaw(Connection),
    budget_workflow: markRaw(Tickets),
    fixed_assets: markRaw(SetUp),
    tax_invoice: markRaw(Money),
    close_consolidation: markRaw(Finished),
  }
  return iconMap[key] || markRaw(TrendCharts)
}

function statusTag(status: string) {
  if (['blocker', 'warning', 'overdue', 'required', 'blocked'].includes(status)) return 'danger'
  if (['partial', 'checking', 'pending', 'preview', 'open', 'watch'].includes(status)) return 'warning'
  if (['ready', 'normal', 'active', 'closed'].includes(status)) return 'success'
  return 'info'
}

function statusColor(status: string) {
  if (['blocker', 'warning', 'overdue', 'required', 'blocked'].includes(status)) return RED
  if (['partial', 'checking', 'pending', 'preview', 'open', 'watch'].includes(status)) return GOLD
  if (['ready', 'normal', 'active', 'closed'].includes(status)) return GREEN
  return '#7A8289'
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    ready: '就绪',
    partial: '部分支持',
    warning: '关注',
    planned: '规划中',
    blocker: '阻断',
    blocked: '阻断',
    checking: '检查中',
    open: '打开',
    preview: '预览',
    normal: '正常',
    watch: '关注',
    overdue: '逾期',
    active: '使用中',
    closed: '已关闭',
  }
  return map[status] || status
}

function priorityClass(priority: string) {
  return {
    p0: priority === 'P0',
    p1: priority === 'P1',
    p2: priority === 'P2',
  }
}

function accountCategoryLabel(category: string) {
  const map: Record<string, string> = {
    asset: '资产',
    liability: '负债',
    equity: '权益',
    revenue: '收入',
    expense: '费用',
  }
  return map[category] || category
}

function directionText(direction: string) {
  return direction === 'credit' ? '贷方' : '借方'
}

function flowDirectionLabel(direction: string) {
  return direction === 'inflow' ? '流入' : '流出'
}

function ledgerTypeLabel(type: string) {
  return type === 'receivable' ? '应收' : '应付'
}

function approvalTag(status: string) {
  if (status === 'required') return 'danger'
  if (status === 'pending') return 'warning'
  return 'success'
}

function approvalLabel(status: string) {
  if (status === 'required') return '需审批'
  if (status === 'pending') return '待复核'
  return '正常'
}

function invoiceTypeLabel(type: string) {
  return type === 'output' ? '销项' : '进项'
}

onMounted(() => {
  applyFallback()
  fetchSuite()
})
</script>

<style scoped lang="scss">
.finance-suite-page {
  display: grid;
  gap: 12px;
}

.suite-toolbar {
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

.suite-kpi-band {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.suite-stat,
.panel,
.module-card {
  background: rgba(255, 253, 249, 0.96);
  border: 1px solid #E5DED4;
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(51, 45, 40, 0.06);
}

.suite-stat {
  display: grid;
  gap: 8px;
  min-height: 112px;
  padding: 14px;

  span {
    color: #756D64;
    font-size: 12px;
    font-weight: 900;
  }

  strong {
    color: #17110D;
    font-size: 30px;
    line-height: 1;
  }

  p {
    margin: 0;
    color: #8A8074;
    font-size: 12px;
    line-height: 1.45;
  }
}

.suite-module-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
}

.module-card {
  position: relative;
  display: grid;
  gap: 7px;
  min-height: 226px;
  padding: 13px;
  color: inherit;
  text-align: left;
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.16s ease, border-color 0.16s ease;

  &::after {
    content: '';
    position: absolute;
    inset: auto 0 0;
    height: 3px;
    background: #7A8289;
  }

  &.ready::after {
    background: #2F8F5B;
  }

  &.partial::after,
  &.planned::after {
    background: #D19A36;
  }

  &.warning::after {
    background: #C81E1E;
  }

  &.active {
    border-color: #C81E1E;
    transform: translateY(-2px);
  }

  strong {
    color: #211A15;
    font-size: 14px;
    font-weight: 900;
  }

  span {
    color: #8A8074;
    font-size: 11px;
    font-weight: 900;
  }

  em {
    color: #17110D;
    font-size: 19px;
    font-style: normal;
    font-weight: 900;
    white-space: nowrap;
  }

  p {
    margin: 0;
    color: #554D46;
    font-size: 12px;
    line-height: 1.45;
  }
}

.module-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;

  b {
    display: grid;
    place-items: center;
    min-width: 32px;
    height: 24px;
    border-radius: 5px;
    background: #211A15;
    color: #fff;
    font-size: 11px;
  }

  .el-icon {
    color: #C81E1E;
    font-size: 18px;
  }
}

.module-foot {
  display: grid;
  gap: 5px;
  align-self: end;

  small {
    color: #756D64;
    font-size: 11px;
    font-weight: 800;
  }
}

.suite-workbench {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(310px, 0.34fr);
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

  span {
    color: #8A8074;
    font-size: 12px;
    font-weight: 700;
  }

  &.compact {
    padding-bottom: 8px;
  }
}

.detail-panel h3 {
  margin: 16px 0 8px;
  color: #211A15;
  font-size: 14px;
  font-weight: 900;
}

.ledger-period-list {
  display: grid;
  gap: 8px;
  padding-top: 12px;
}

.period-row {
  display: grid;
  grid-template-columns: 120px repeat(3, minmax(120px, 1fr)) auto;
  gap: 10px;
  align-items: center;
  padding: 11px;
  background: #FAF8F4;
  border: 1px solid #EEE7DC;
  border-radius: 6px;

  strong {
    color: #211A15;
    font-size: 13px;
    font-weight: 900;
  }

  span {
    color: #554D46;
    font-size: 12px;
    font-weight: 800;
  }

  p {
    grid-column: 1 / -1;
    margin: 0;
    color: #8A8074;
    font-size: 12px;
  }
}

.suite-table {
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
    vertical-align: top;
    white-space: nowrap;
  }

  th {
    color: #8A8074;
    font-weight: 900;
  }

  th:first-child,
  td:first-child,
  th:nth-child(2),
  td:nth-child(2) {
    text-align: left;
  }

  .table-empty {
    color: #8A8074;
    font-weight: 800;
    text-align: center;
  }
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

@media (max-width: 1480px) {
  .suite-module-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .suite-workbench {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1040px) {
  .suite-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .suite-kpi-band,
  .suite-module-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .freshness-line {
    justify-content: flex-start;
    flex-direction: column;
    gap: 4px;
  }

  .period-row {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .suite-kpi-band,
  .suite-module-grid {
    grid-template-columns: 1fr;
  }

  .toolbar-controls {
    justify-content: flex-start;
  }

  .suite-table {
    display: block;
    overflow-x: auto;
  }
}
</style>
