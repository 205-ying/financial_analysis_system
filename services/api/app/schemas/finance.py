"""
Finance operations center schemas.

The module models a read-only finance cockpit built on the existing restaurant
business data. It avoids introducing accounting ledger writes before the system
has journal-entry and period-close ownership.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FinanceMetricCard(BaseModel):
    """Top-level finance metric."""

    key: str = Field(..., description="Metric key")
    label: str = Field(..., description="Metric label")
    value: float = Field(0.0, description="Metric value")
    unit: str = Field("", description="Metric unit")
    tone: str = Field("neutral", description="Visual tone")
    description: str = Field("", description="Business explanation")


class CashFlowPoint(BaseModel):
    """Daily cash movement."""

    date: str = Field(..., description="Business date")
    inflow: float = Field(0.0, description="Estimated cash inflow")
    outflow: float = Field(0.0, description="Estimated cash outflow")
    net: float = Field(0.0, description="Net cash movement")
    cumulative: float = Field(0.0, description="Cumulative net movement")


class WorkingCapitalItem(BaseModel):
    """Receivable/payable pressure item."""

    key: str = Field(..., description="Item key")
    name: str = Field(..., description="Item name")
    amount: float = Field(0.0, description="Amount")
    count: int = Field(0, description="Record count")
    risk_level: str = Field("low", description="Risk level: low/medium/high")
    suggestion: str = Field("", description="Recommended action")


class BudgetControlItem(BaseModel):
    """Budget execution item."""

    name: str = Field(..., description="Expense category")
    actual: float = Field(0.0, description="Actual spend")
    budget: float = Field(0.0, description="Budget amount")
    variance: float = Field(0.0, description="Actual minus budget")
    execution_rate: float = Field(0.0, description="Actual / budget in percent")
    status: str = Field("normal", description="normal/watch/over")


class FinanceCapability(BaseModel):
    """Finance system capability maturity item."""

    key: str = Field(..., description="Capability key")
    name: str = Field(..., description="Capability name")
    category: str = Field(..., description="Capability category")
    status: str = Field(..., description="ready/partial/planned")
    maturity_score: int = Field(0, ge=0, le=100, description="Maturity score")
    current_support: str = Field("", description="Current project support")
    next_actions: list[str] = Field(default_factory=list, description="Next actions")
    evidence_metrics: list[str] = Field(default_factory=list, description="Evidence")


class FinanceActionItem(BaseModel):
    """Prioritized finance action."""

    priority: str = Field(..., description="P0/P1/P2")
    title: str = Field(..., description="Action title")
    owner: str = Field(..., description="Suggested owner")
    reason: str = Field(..., description="Why this matters")
    due_hint: str = Field(..., description="Suggested timing")


class FinanceCloseChecklistItem(BaseModel):
    """Period-close readiness checklist item."""

    key: str = Field(..., description="Checklist key")
    name: str = Field(..., description="Checklist item name")
    owner: str = Field(..., description="Suggested owner")
    status: str = Field("ready", description="ready/warning/blocker/planned")
    ready_count: int = Field(0, description="Ready record count")
    issue_count: int = Field(0, description="Issue record count")
    amount: float = Field(0.0, description="Issue or exposure amount")
    description: str = Field("", description="Current-state explanation")
    next_step: str = Field("", description="Recommended next step")


class BankReconciliationItem(BaseModel):
    """Bank reconciliation preparation item."""

    channel: str = Field(..., description="Payment channel or account")
    direction: str = Field(..., description="inflow/outflow")
    expected_amount: float = Field(0.0, description="Expected statement amount")
    record_count: int = Field(0, description="Source record count")
    unmatched_count: int = Field(0, description="Records needing reconciliation")
    unmatched_amount: float = Field(0.0, description="Amount needing reconciliation")
    status: str = Field("ready", description="ready/warning/blocker")
    account_hint: str = Field("", description="Account or data-quality hint")


class LedgerReadinessItem(BaseModel):
    """General-ledger preparation item."""

    key: str = Field(..., description="Ledger preparation key")
    name: str = Field(..., description="Ledger preparation name")
    status: str = Field("ready", description="ready/warning/blocker/planned")
    coverage: float = Field(0.0, description="Coverage percentage")
    source: str = Field("", description="Source module or table")
    remark: str = Field("", description="Readiness remark")


class FinanceOperationsOverview(BaseModel):
    """Finance operations center overview."""

    generated_at: datetime = Field(..., description="Generation time")
    cards: list[FinanceMetricCard] = Field(default_factory=list)
    cash_flow: list[CashFlowPoint] = Field(default_factory=list)
    working_capital: list[WorkingCapitalItem] = Field(default_factory=list)
    budget_controls: list[BudgetControlItem] = Field(default_factory=list)
    capability_matrix: list[FinanceCapability] = Field(default_factory=list)
    action_items: list[FinanceActionItem] = Field(default_factory=list)


class FinanceCloseReadinessOverview(BaseModel):
    """Period-close preparation overview."""

    generated_at: datetime = Field(..., description="Generation time")
    period_start: str = Field(..., description="Period start date")
    period_end: str = Field(..., description="Period end date")
    close_score: int = Field(0, ge=0, le=100, description="Close readiness score")
    checklist: list[FinanceCloseChecklistItem] = Field(default_factory=list)
    bank_reconciliation: list[BankReconciliationItem] = Field(default_factory=list)
    ledger_readiness: list[LedgerReadinessItem] = Field(default_factory=list)
    action_items: list[FinanceActionItem] = Field(default_factory=list)


class FinanceSuiteModule(BaseModel):
    """Remaining finance capability module summary."""

    key: str = Field(..., description="Module key")
    name: str = Field(..., description="Module name")
    priority: str = Field(..., description="P0/P1/P2")
    status: str = Field("ready", description="ready/partial/warning/planned")
    maturity_score: int = Field(0, ge=0, le=100, description="Maturity score")
    metric_label: str = Field(..., description="Primary metric label")
    metric_value: float = Field(0.0, description="Primary metric value")
    issue_count: int = Field(0, description="Issue count")
    description: str = Field("", description="Module description")


class GeneralLedgerPeriodItem(BaseModel):
    """Accounting period and ledger preparation row."""

    period: str = Field(..., description="Accounting period")
    status: str = Field("open", description="open/checking/closed")
    revenue_amount: float = Field(0.0, description="Revenue amount")
    expense_amount: float = Field(0.0, description="Expense amount")
    journal_preview_count: int = Field(0, description="Preview journal count")
    unposted_count: int = Field(0, description="Unposted preview count")
    next_step: str = Field("", description="Next step")


class ChartOfAccountItem(BaseModel):
    """Chart of account row."""

    code: str = Field(..., description="Account code")
    name: str = Field(..., description="Account name")
    category: str = Field(..., description="asset/liability/equity/revenue/expense")
    balance_direction: str = Field(..., description="debit/credit")
    mapped_source: str = Field("", description="Mapped source")
    status: str = Field("ready", description="ready/partial/planned")


class JournalEntryPreviewItem(BaseModel):
    """Generated journal-entry preview from source data."""

    source_type: str = Field(..., description="orders/expenses/budget/close")
    entry_date: str = Field(..., description="Entry date")
    summary: str = Field(..., description="Entry summary")
    debit_account: str = Field(..., description="Debit account")
    credit_account: str = Field(..., description="Credit account")
    amount: float = Field(0.0, description="Entry amount")
    status: str = Field("preview", description="preview/blocked/ready")


class BankAccountItem(BaseModel):
    """Bank account or payment channel row."""

    name: str = Field(..., description="Account/channel name")
    channel: str = Field(..., description="Payment channel")
    direction: str = Field(..., description="inflow/outflow")
    statement_amount: float = Field(0.0, description="Expected statement amount")
    matched_amount: float = Field(0.0, description="Matched amount")
    unmatched_amount: float = Field(0.0, description="Unmatched amount")
    unmatched_count: int = Field(0, description="Unmatched count")
    status: str = Field("ready", description="ready/warning/blocker")


class CounterpartyLedgerItem(BaseModel):
    """Accounts receivable/payable ledger row."""

    counterparty: str = Field(..., description="Customer/vendor/channel")
    ledger_type: str = Field(..., description="receivable/payable")
    amount: float = Field(0.0, description="Open amount")
    record_count: int = Field(0, description="Record count")
    aging_bucket: str = Field(..., description="Aging bucket")
    status: str = Field("normal", description="normal/watch/overdue")
    next_step: str = Field("", description="Recommended action")


class BudgetVersionItem(BaseModel):
    """Budget version and approval row."""

    version_name: str = Field(..., description="Budget version")
    scope: str = Field(..., description="Scope")
    budget_amount: float = Field(0.0, description="Budget amount")
    actual_amount: float = Field(0.0, description="Actual amount")
    variance_amount: float = Field(0.0, description="Variance")
    approval_status: str = Field("normal", description="normal/pending/required")
    owner: str = Field("预算负责人", description="Owner")


class FixedAssetItem(BaseModel):
    """Fixed asset card row."""

    asset_name: str = Field(..., description="Asset name")
    store_name: str = Field(..., description="Store")
    category: str = Field(..., description="Asset category")
    original_value: float = Field(0.0, description="Original value")
    monthly_depreciation: float = Field(0.0, description="Monthly depreciation")
    net_value: float = Field(0.0, description="Net value")
    status: str = Field("active", description="active/checking/planned")


class TaxInvoiceItem(BaseModel):
    """Tax and invoice ledger row."""

    invoice_type: str = Field(..., description="output/input")
    source: str = Field(..., description="Source")
    taxable_amount: float = Field(0.0, description="Taxable amount")
    tax_rate: float = Field(0.0, description="Tax rate")
    tax_amount: float = Field(0.0, description="Tax amount")
    invoice_count: int = Field(0, description="Invoice count")
    missing_invoice_count: int = Field(0, description="Missing invoice count")
    status: str = Field("ready", description="ready/warning/blocker")


class CloseConsolidationItem(BaseModel):
    """Financial close and consolidation row."""

    store_name: str = Field(..., description="Store or consolidation scope")
    revenue_amount: float = Field(0.0, description="Revenue")
    expense_amount: float = Field(0.0, description="Expense")
    profit_amount: float = Field(0.0, description="Profit")
    close_status: str = Field("checking", description="open/checking/ready/closed")
    blocker_count: int = Field(0, description="Blocker count")
    consolidation_note: str = Field("", description="Consolidation note")


class FinanceSuiteOverview(BaseModel):
    """All remaining finance capabilities in one operational workbench."""

    generated_at: datetime = Field(..., description="Generation time")
    period_start: str = Field(..., description="Period start")
    period_end: str = Field(..., description="Period end")
    modules: list[FinanceSuiteModule] = Field(default_factory=list)
    general_ledger_periods: list[GeneralLedgerPeriodItem] = Field(default_factory=list)
    chart_of_accounts: list[ChartOfAccountItem] = Field(default_factory=list)
    journal_entry_previews: list[JournalEntryPreviewItem] = Field(default_factory=list)
    bank_accounts: list[BankAccountItem] = Field(default_factory=list)
    counterparty_ledgers: list[CounterpartyLedgerItem] = Field(default_factory=list)
    budget_versions: list[BudgetVersionItem] = Field(default_factory=list)
    fixed_assets: list[FixedAssetItem] = Field(default_factory=list)
    tax_invoices: list[TaxInvoiceItem] = Field(default_factory=list)
    close_consolidation: list[CloseConsolidationItem] = Field(default_factory=list)
    action_items: list[FinanceActionItem] = Field(default_factory=list)
