/**
 * 财务运营中心类型定义
 */

export interface FinanceMetricCard {
  key: string
  label: string
  value: number
  unit: string
  tone: 'positive' | 'warning' | 'danger' | 'neutral' | string
  description: string
}

export interface CashFlowPoint {
  date: string
  inflow: number
  outflow: number
  net: number
  cumulative: number
}

export interface WorkingCapitalItem {
  key: string
  name: string
  amount: number
  count: number
  risk_level: 'low' | 'medium' | 'high' | string
  suggestion: string
}

export interface BudgetControlItem {
  name: string
  actual: number
  budget: number
  variance: number
  execution_rate: number
  status: 'normal' | 'watch' | 'over' | string
}

export interface FinanceCapability {
  key: string
  name: string
  category: string
  status: 'ready' | 'partial' | 'planned' | string
  maturity_score: number
  current_support: string
  next_actions: string[]
  evidence_metrics: string[]
}

export interface FinanceActionItem {
  priority: 'P0' | 'P1' | 'P2' | string
  title: string
  owner: string
  reason: string
  due_hint: string
}

export interface FinanceCloseChecklistItem {
  key: string
  name: string
  owner: string
  status: 'ready' | 'warning' | 'blocker' | 'planned' | string
  ready_count: number
  issue_count: number
  amount: number
  description: string
  next_step: string
}

export interface BankReconciliationItem {
  channel: string
  direction: 'inflow' | 'outflow' | string
  expected_amount: number
  record_count: number
  unmatched_count: number
  unmatched_amount: number
  status: 'ready' | 'warning' | 'blocker' | string
  account_hint: string
}

export interface LedgerReadinessItem {
  key: string
  name: string
  status: 'ready' | 'warning' | 'blocker' | 'planned' | string
  coverage: number
  source: string
  remark: string
}

export interface FinanceOperationsOverview {
  generated_at: string
  cards: FinanceMetricCard[]
  cash_flow: CashFlowPoint[]
  working_capital: WorkingCapitalItem[]
  budget_controls: BudgetControlItem[]
  capability_matrix: FinanceCapability[]
  action_items: FinanceActionItem[]
}

export interface FinanceCloseReadinessOverview {
  generated_at: string
  period_start: string
  period_end: string
  close_score: number
  checklist: FinanceCloseChecklistItem[]
  bank_reconciliation: BankReconciliationItem[]
  ledger_readiness: LedgerReadinessItem[]
  action_items: FinanceActionItem[]
}

export interface FinanceOperationsQuery {
  start_date: string
  end_date: string
  store_id?: number
}

export interface FinanceSuiteModule {
  key: string
  name: string
  priority: 'P0' | 'P1' | 'P2' | string
  status: 'ready' | 'partial' | 'warning' | 'planned' | string
  maturity_score: number
  metric_label: string
  metric_value: number
  issue_count: number
  description: string
}

export interface GeneralLedgerPeriodItem {
  period: string
  status: string
  revenue_amount: number
  expense_amount: number
  journal_preview_count: number
  unposted_count: number
  next_step: string
}

export interface ChartOfAccountItem {
  code: string
  name: string
  category: string
  balance_direction: string
  mapped_source: string
  status: string
}

export interface JournalEntryPreviewItem {
  source_type: string
  entry_date: string
  summary: string
  debit_account: string
  credit_account: string
  amount: number
  status: string
}

export interface BankAccountItem {
  name: string
  channel: string
  direction: string
  statement_amount: number
  matched_amount: number
  unmatched_amount: number
  unmatched_count: number
  status: string
}

export interface CounterpartyLedgerItem {
  counterparty: string
  ledger_type: string
  amount: number
  record_count: number
  aging_bucket: string
  status: string
  next_step: string
}

export interface BudgetVersionItem {
  version_name: string
  scope: string
  budget_amount: number
  actual_amount: number
  variance_amount: number
  approval_status: string
  owner: string
}

export interface FixedAssetItem {
  asset_name: string
  store_name: string
  category: string
  original_value: number
  monthly_depreciation: number
  net_value: number
  status: string
}

export interface TaxInvoiceItem {
  invoice_type: string
  source: string
  taxable_amount: number
  tax_rate: number
  tax_amount: number
  invoice_count: number
  missing_invoice_count: number
  status: string
}

export interface CloseConsolidationItem {
  store_name: string
  revenue_amount: number
  expense_amount: number
  profit_amount: number
  close_status: string
  blocker_count: number
  consolidation_note: string
}

export interface FinanceSuiteOverview {
  generated_at: string
  period_start: string
  period_end: string
  modules: FinanceSuiteModule[]
  general_ledger_periods: GeneralLedgerPeriodItem[]
  chart_of_accounts: ChartOfAccountItem[]
  journal_entry_previews: JournalEntryPreviewItem[]
  bank_accounts: BankAccountItem[]
  counterparty_ledgers: CounterpartyLedgerItem[]
  budget_versions: BudgetVersionItem[]
  fixed_assets: FixedAssetItem[]
  tax_invoices: TaxInvoiceItem[]
  close_consolidation: CloseConsolidationItem[]
  action_items: FinanceActionItem[]
}
