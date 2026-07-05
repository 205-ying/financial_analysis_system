"""
Read-only finance operations aggregations.

This service turns the current operational tables into finance-management views:
cash movement, working-capital pressure, budget execution, and capability
maturity. It intentionally does not mutate accounting records.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy import case, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.budget import Budget
from app.models.expense import ExpenseRecord, ExpenseType
from app.models.import_job import DataImportJob, ImportJobStatus
from app.models.order import OrderHeader
from app.models.store import Store
from app.schemas.finance import (
    BankReconciliationItem,
    BudgetControlItem,
    BankAccountItem,
    BudgetVersionItem,
    CashFlowPoint,
    ChartOfAccountItem,
    CloseConsolidationItem,
    CounterpartyLedgerItem,
    FinanceActionItem,
    FinanceCapability,
    FinanceCloseChecklistItem,
    FinanceCloseReadinessOverview,
    FinanceMetricCard,
    FinanceOperationsOverview,
    FinanceSuiteModule,
    FinanceSuiteOverview,
    FixedAssetItem,
    GeneralLedgerPeriodItem,
    JournalEntryPreviewItem,
    LedgerReadinessItem,
    TaxInvoiceItem,
    WorkingCapitalItem,
)


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


def _risk_by_amount(amount: float, base: float) -> str:
    if base <= 0:
        return "low" if amount <= 0 else "medium"
    ratio = amount / base
    if ratio >= 0.12:
        return "high"
    if ratio >= 0.06:
        return "medium"
    return "low"


def _iter_dates(start_date: date, end_date: date) -> list[date]:
    days = (end_date - start_date).days
    return [start_date + timedelta(days=offset) for offset in range(days + 1)]


def _coverage(total_count: int, issue_count: int) -> float:
    if total_count <= 0:
        return 0.0
    return round(max(0, total_count - issue_count) / total_count * 100, 1)


def _readiness_status(
    issue_count: int,
    amount: float = 0.0,
    *,
    warning_only: bool = False,
) -> str:
    if issue_count <= 0 and amount <= 0:
        return "ready"
    return "warning" if warning_only else "blocker"


async def _daily_inflows(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> dict[date, float]:
    query = (
        select(OrderHeader.biz_date, func.sum(OrderHeader.net_amount))
        .where(OrderHeader.biz_date >= start_date)
        .where(OrderHeader.biz_date <= end_date)
        .where(OrderHeader.status.notin_(["cancelled", "refunded"]))
        .group_by(OrderHeader.biz_date)
        .order_by(OrderHeader.biz_date)
    )
    if accessible_store_ids is not None:
        query = query.where(OrderHeader.store_id.in_(accessible_store_ids))

    rows = (await db.execute(query)).all()
    return {row[0]: _to_float(row[1]) for row in rows}


async def _daily_outflows(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> dict[date, float]:
    query = (
        select(ExpenseRecord.biz_date, func.sum(ExpenseRecord.amount))
        .where(ExpenseRecord.biz_date >= start_date)
        .where(ExpenseRecord.biz_date <= end_date)
        .where(ExpenseRecord.status.in_(["approved", "paid"]))
        .where(ExpenseRecord.is_deleted.is_(False))
        .group_by(ExpenseRecord.biz_date)
        .order_by(ExpenseRecord.biz_date)
    )
    if accessible_store_ids is not None:
        query = query.where(ExpenseRecord.store_id.in_(accessible_store_ids))

    rows = (await db.execute(query)).all()
    return {row[0]: _to_float(row[1]) for row in rows}


async def _working_capital(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
    revenue_base: float,
) -> list[WorkingCapitalItem]:
    receivable_query = (
        select(func.sum(OrderHeader.net_amount), func.count(OrderHeader.id))
        .where(OrderHeader.biz_date >= start_date)
        .where(OrderHeader.biz_date <= end_date)
        .where(OrderHeader.status.notin_(["completed", "cancelled", "refunded"]))
    )
    settlement_query = (
        select(func.sum(OrderHeader.net_amount), func.count(OrderHeader.id))
        .where(OrderHeader.biz_date >= start_date)
        .where(OrderHeader.biz_date <= end_date)
        .where(OrderHeader.status.notin_(["cancelled", "refunded"]))
        .where(OrderHeader.payment_time.is_(None))
    )
    payable_query = (
        select(func.sum(ExpenseRecord.amount), func.count(ExpenseRecord.id))
        .where(ExpenseRecord.biz_date >= start_date)
        .where(ExpenseRecord.biz_date <= end_date)
        .where(ExpenseRecord.status.in_(["submitted", "approved"]))
        .where(ExpenseRecord.is_deleted.is_(False))
    )
    if accessible_store_ids is not None:
        receivable_query = receivable_query.where(
            OrderHeader.store_id.in_(accessible_store_ids)
        )
        settlement_query = settlement_query.where(
            OrderHeader.store_id.in_(accessible_store_ids)
        )
        payable_query = payable_query.where(
            ExpenseRecord.store_id.in_(accessible_store_ids)
        )

    receivable = (await db.execute(receivable_query)).one()
    settlement = (await db.execute(settlement_query)).one()
    payable = (await db.execute(payable_query)).one()

    receivable_amount = _to_float(receivable[0])
    settlement_amount = _to_float(settlement[0])
    payable_amount = _to_float(payable[0])

    return [
        WorkingCapitalItem(
            key="receivables",
            name="应收/待确认营业款",
            amount=round(receivable_amount, 2),
            count=int(receivable[1] or 0),
            risk_level=_risk_by_amount(receivable_amount, revenue_base),
            suggestion="跟进未完结订单，优先核对高金额堂食/外卖结算差异。",
        ),
        WorkingCapitalItem(
            key="unsettled_orders",
            name="未记录收款时间订单",
            amount=round(settlement_amount, 2),
            count=int(settlement[1] or 0),
            risk_level=_risk_by_amount(settlement_amount, revenue_base),
            suggestion="补齐支付流水时间，避免收入确认与银行对账脱节。",
        ),
        WorkingCapitalItem(
            key="payables",
            name="应付/待付款费用",
            amount=round(payable_amount, 2),
            count=int(payable[1] or 0),
            risk_level=_risk_by_amount(payable_amount, revenue_base),
            suggestion="按供应商和账期排款，避免审批后付款堆积。",
        ),
    ]


async def _budget_controls(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> list[BudgetControlItem]:
    start_ym = start_date.year * 100 + start_date.month
    end_ym = end_date.year * 100 + end_date.month

    budget_query = (
        select(ExpenseType.name, func.sum(Budget.amount))
        .select_from(Budget)
        .join(ExpenseType, Budget.expense_type_id == ExpenseType.id)
        .where((Budget.year * 100 + Budget.month) >= start_ym)
        .where((Budget.year * 100 + Budget.month) <= end_ym)
        .group_by(ExpenseType.name)
    )
    actual_query = (
        select(ExpenseType.name, func.sum(ExpenseRecord.amount))
        .select_from(ExpenseRecord)
        .join(ExpenseType, ExpenseRecord.expense_type_id == ExpenseType.id)
        .where(ExpenseRecord.biz_date >= start_date)
        .where(ExpenseRecord.biz_date <= end_date)
        .where(ExpenseRecord.status.in_(["approved", "paid"]))
        .where(ExpenseRecord.is_deleted.is_(False))
        .group_by(ExpenseType.name)
    )
    if accessible_store_ids is not None:
        budget_query = budget_query.where(Budget.store_id.in_(accessible_store_ids))
        actual_query = actual_query.where(
            ExpenseRecord.store_id.in_(accessible_store_ids)
        )

    budget_rows = (await db.execute(budget_query)).all()
    actual_rows = (await db.execute(actual_query)).all()
    budgets = defaultdict(float, {row[0]: _to_float(row[1]) for row in budget_rows})
    actuals = defaultdict(float, {row[0]: _to_float(row[1]) for row in actual_rows})

    names = sorted(set(budgets) | set(actuals))
    items: list[BudgetControlItem] = []
    for name in names:
        budget = budgets[name]
        actual = actuals[name]
        variance = actual - budget
        rate = round(actual / budget * 100, 2) if budget > 0 else 0.0
        if budget > 0 and rate >= 105:
            status = "over"
        elif budget > 0 and rate >= 90:
            status = "watch"
        else:
            status = "normal"
        items.append(
            BudgetControlItem(
                name=name,
                actual=round(actual, 2),
                budget=round(budget, 2),
                variance=round(variance, 2),
                execution_rate=rate,
                status=status,
            )
        )

    return sorted(items, key=lambda item: item.execution_rate, reverse=True)[:8]


def _capability_matrix(
    revenue: float,
    expense: float,
    budget_items: list[BudgetControlItem],
    working_capital: list[WorkingCapitalItem],
) -> list[FinanceCapability]:
    budget_ready = bool(budget_items)
    has_working_capital_risk = any(item.amount > 0 for item in working_capital)
    return [
        FinanceCapability(
            key="cash_flow",
            name="现金流监控",
            category="资金",
            status="ready" if revenue or expense else "partial",
            maturity_score=82 if revenue or expense else 58,
            current_support="按订单实收与已审批/已支付费用生成日度现金流曲线。",
            next_actions=["接入银行流水", "增加账户余额快照", "建立收付款核销关系"],
            evidence_metrics=["营业现金流入", "经营现金流出", "累计净现金流"],
        ),
        FinanceCapability(
            key="working_capital",
            name="应收应付与结算",
            category="往来",
            status="partial",
            maturity_score=68 if has_working_capital_risk else 62,
            current_support="从未完结订单、未记录收款时间订单和待付款费用估算风险。",
            next_actions=["补充客户/供应商账期", "建立发票与收付款状态", "按账龄输出催收/排款清单"],
            evidence_metrics=["待确认营业款", "未记录收款订单", "待付款费用"],
        ),
        FinanceCapability(
            key="budget_control",
            name="预算控制",
            category="经营控制",
            status="ready" if budget_ready else "partial",
            maturity_score=78 if budget_ready else 55,
            current_support="按费用科目对比预算、实际、差异和执行率。",
            next_actions=["预算版本管理", "超预算审批流", "滚动预测"],
            evidence_metrics=["预算执行率", "超预算科目", "费用结构"],
        ),
        FinanceCapability(
            key="general_ledger",
            name="总账与会计期间",
            category="核算",
            status="planned",
            maturity_score=35,
            current_support="目前以经营分析口径聚合，还没有凭证、科目余额和关账流程。",
            next_actions=["设计会计科目表", "建立凭证分录", "增加期间关账与反关账权限"],
            evidence_metrics=["收入", "费用", "利润"],
        ),
        FinanceCapability(
            key="fixed_assets",
            name="固定资产",
            category="资产",
            status="planned",
            maturity_score=28,
            current_support="暂未区分设备、装修、摊销和折旧。",
            next_actions=["建设资产卡片", "折旧规则", "盘点与处置流程"],
            evidence_metrics=["门店面积", "费用记录"],
        ),
        FinanceCapability(
            key="tax_compliance",
            name="税务与合规",
            category="合规",
            status="planned",
            maturity_score=30,
            current_support="已有审计日志和基础报表，税率、发票勾稽和纳税申报尚未建模。",
            next_actions=["增加发票台账", "维护税率规则", "生成税务申报辅助报表"],
            evidence_metrics=["发票号", "费用审批", "审计日志"],
        ),
    ]


def _action_items(
    cards: list[FinanceMetricCard],
    budget_items: list[BudgetControlItem],
    working_capital: list[WorkingCapitalItem],
) -> list[FinanceActionItem]:
    actions: list[FinanceActionItem] = []
    net_cash = next((card.value for card in cards if card.key == "net_cash"), 0)
    if net_cash < 0:
        actions.append(
            FinanceActionItem(
                priority="P0",
                title="复核经营现金流缺口",
                owner="财务负责人",
                reason="查询期内现金流为负，需要确认费用支付节奏和收入到账。",
                due_hint="今日下班前",
            )
        )
    for item in budget_items[:3]:
        if item.status == "over":
            actions.append(
                FinanceActionItem(
                    priority="P1",
                    title=f"冻结或复核「{item.name}」新增支出",
                    owner="预算负责人",
                    reason=f"执行率 {item.execution_rate:.1f}%，已超过预算控制线。",
                    due_hint="2 个工作日内",
                )
            )
    for item in working_capital:
        if item.risk_level == "high":
            actions.append(
                FinanceActionItem(
                    priority="P1",
                    title=f"处理{item.name}",
                    owner="出纳/会计",
                    reason=f"未闭环金额 {item.amount:.2f} 元，影响资金预测准确性。",
                    due_hint="本周内",
                )
            )

    if not actions:
        actions.append(
            FinanceActionItem(
                priority="P2",
                title="完善财务系统下一阶段基础数据",
                owner="财务信息化负责人",
                reason="当前经营分析可用，下一阶段应补齐总账、账期、资产和税务台账。",
                due_hint="本月规划会",
            )
        )
    return actions[:6]


async def get_finance_operations_overview(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
) -> FinanceOperationsOverview:
    """Build the finance operations overview from existing business tables."""

    inflows = await _daily_inflows(db, start_date, end_date, accessible_store_ids)
    outflows = await _daily_outflows(db, start_date, end_date, accessible_store_ids)

    cumulative = 0.0
    cash_flow: list[CashFlowPoint] = []
    for biz_date in _iter_dates(start_date, end_date):
        inflow = inflows.get(biz_date, 0.0)
        outflow = outflows.get(biz_date, 0.0)
        net = inflow - outflow
        cumulative += net
        cash_flow.append(
            CashFlowPoint(
                date=biz_date.isoformat(),
                inflow=round(inflow, 2),
                outflow=round(outflow, 2),
                net=round(net, 2),
                cumulative=round(cumulative, 2),
            )
        )

    total_inflow = round(sum(inflows.values()), 2)
    total_outflow = round(sum(outflows.values()), 2)
    net_cash = round(total_inflow - total_outflow, 2)
    working_capital = await _working_capital(
        db, start_date, end_date, accessible_store_ids, total_inflow
    )
    budget_controls = await _budget_controls(
        db, start_date, end_date, accessible_store_ids
    )
    total_budget = sum(item.budget for item in budget_controls)
    total_actual = sum(item.actual for item in budget_controls)
    budget_rate = round(total_actual / total_budget * 100, 2) if total_budget else 0.0

    open_receivable = next(
        (item.amount for item in working_capital if item.key == "receivables"), 0.0
    )
    open_payable = next(
        (item.amount for item in working_capital if item.key == "payables"), 0.0
    )
    cards = [
        FinanceMetricCard(
            key="cash_inflow",
            label="经营现金流入",
            value=total_inflow,
            unit="元",
            tone="positive",
            description="订单净额估算的经营现金流入。",
        ),
        FinanceMetricCard(
            key="cash_outflow",
            label="经营现金流出",
            value=total_outflow,
            unit="元",
            tone="warning",
            description="已审批/已支付费用估算的经营现金流出。",
        ),
        FinanceMetricCard(
            key="net_cash",
            label="净现金流",
            value=net_cash,
            unit="元",
            tone="positive" if net_cash >= 0 else "danger",
            description="现金流入减现金流出。",
        ),
        FinanceMetricCard(
            key="budget_execution",
            label="预算执行率",
            value=budget_rate,
            unit="%",
            tone="danger" if budget_rate >= 105 else "neutral",
            description="查询期内可匹配预算科目的实际/预算。",
        ),
        FinanceMetricCard(
            key="open_receivable",
            label="待确认营业款",
            value=open_receivable,
            unit="元",
            tone="warning" if open_receivable > 0 else "neutral",
            description="未完结订单对应的收入风险。",
        ),
        FinanceMetricCard(
            key="open_payable",
            label="待付款费用",
            value=open_payable,
            unit="元",
            tone="warning" if open_payable > 0 else "neutral",
            description="已提交/已审批但未支付的费用压力。",
        ),
    ]

    capability_matrix = _capability_matrix(
        total_inflow, total_outflow, budget_controls, working_capital
    )
    return FinanceOperationsOverview(
        generated_at=datetime.now(tz=UTC),
        cards=cards,
        cash_flow=cash_flow,
        working_capital=working_capital,
        budget_controls=budget_controls,
        capability_matrix=capability_matrix,
        action_items=_action_items(cards, budget_controls, working_capital),
    )


async def _close_checklist(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> tuple[list[FinanceCloseChecklistItem], dict[str, float | int]]:
    order_conditions = [
        OrderHeader.biz_date >= start_date,
        OrderHeader.biz_date <= end_date,
        OrderHeader.status.notin_(["cancelled", "refunded"]),
    ]
    expense_conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date,
        ExpenseRecord.is_deleted.is_(False),
    ]
    if accessible_store_ids is not None:
        order_conditions.append(OrderHeader.store_id.in_(accessible_store_ids))
        expense_conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))

    order_row = (
        await db.execute(
            select(
                func.count(OrderHeader.id),
                func.sum(OrderHeader.net_amount),
                func.sum(
                    case((OrderHeader.payment_time.is_(None), 1), else_=0)
                ),
                func.sum(
                    case(
                        (OrderHeader.payment_time.is_(None), OrderHeader.net_amount),
                        else_=0,
                    )
                ),
                func.sum(
                    case((OrderHeader.status != "completed", 1), else_=0)
                ),
                func.sum(
                    case(
                        (OrderHeader.status != "completed", OrderHeader.net_amount),
                        else_=0,
                    )
                ),
            ).where(*order_conditions)
        )
    ).one()

    expense_row = (
        await db.execute(
            select(
                func.count(ExpenseRecord.id),
                func.sum(ExpenseRecord.amount),
                func.sum(
                    case(
                        (
                            ExpenseRecord.status.in_(
                                ["draft", "submitted", "rejected"]
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                func.sum(
                    case(
                        (
                            ExpenseRecord.status.in_(
                                ["draft", "submitted", "rejected"]
                            ),
                            ExpenseRecord.amount,
                        ),
                        else_=0,
                    )
                ),
                func.sum(
                    case((ExpenseRecord.status == "approved", 1), else_=0)
                ),
                func.sum(
                    case(
                        (ExpenseRecord.status == "approved", ExpenseRecord.amount),
                        else_=0,
                    )
                ),
                func.sum(
                    case(
                        (
                            func.coalesce(ExpenseRecord.invoice_no, "") == "",
                            1,
                        ),
                        else_=0,
                    )
                ),
            ).where(*expense_conditions)
        )
    ).one()

    budget_conditions = [
        (Budget.year * 100 + Budget.month) >= start_date.year * 100 + start_date.month,
        (Budget.year * 100 + Budget.month) <= end_date.year * 100 + end_date.month,
    ]
    if accessible_store_ids is not None:
        budget_conditions.append(Budget.store_id.in_(accessible_store_ids))
    budget_count = int(
        (await db.execute(select(func.count(Budget.id)).where(*budget_conditions))).scalar()
        or 0
    )

    latest_import = (
        await db.execute(select(DataImportJob).order_by(desc(DataImportJob.created_at)).limit(1))
    ).scalar_one_or_none()
    import_issue_count = int(
        (
            await db.execute(
                select(func.count(DataImportJob.id)).where(
                    DataImportJob.status.in_(
                        [
                            ImportJobStatus.PENDING,
                            ImportJobStatus.RUNNING,
                            ImportJobStatus.PARTIAL_FAIL,
                            ImportJobStatus.FAIL,
                        ]
                    )
                )
            )
        ).scalar()
        or 0
    )

    period_start = datetime.combine(start_date, time.min)
    period_end = datetime.combine(end_date, time.max)
    audit_count = int(
        (
            await db.execute(
                select(func.count(AuditLog.id))
                .where(AuditLog.created_at >= period_start)
                .where(AuditLog.created_at <= period_end)
            )
        ).scalar()
        or 0
    )

    order_count = int(order_row[0] or 0)
    order_amount = _to_float(order_row[1])
    missing_payment_count = int(order_row[2] or 0)
    missing_payment_amount = _to_float(order_row[3])
    open_order_count = int(order_row[4] or 0)
    open_order_amount = _to_float(order_row[5])

    expense_count = int(expense_row[0] or 0)
    expense_amount = _to_float(expense_row[1])
    pending_expense_count = int(expense_row[2] or 0)
    pending_expense_amount = _to_float(expense_row[3])
    approved_unpaid_count = int(expense_row[4] or 0)
    approved_unpaid_amount = _to_float(expense_row[5])
    missing_invoice_count = int(expense_row[6] or 0)

    import_status = "warning"
    import_description = "尚未发现导入批次，无法从导入任务追溯本期数据来源。"
    import_next_step = "用导入中心沉淀订单、费用、门店等批次记录。"
    import_ready_rows = 0
    import_issue_rows = import_issue_count
    if latest_import:
        latest_status = getattr(latest_import.status, "value", latest_import.status)
        import_ready_rows = int(latest_import.success_rows or 0)
        import_issue_rows = import_issue_count + int(latest_import.fail_rows or 0)
        import_status = "ready" if import_issue_rows == 0 else "warning"
        import_description = (
            f"最近导入任务：{latest_import.job_name}，状态 {latest_status}，"
            f"成功 {latest_import.success_rows} 行，失败 {latest_import.fail_rows} 行。"
        )
        import_next_step = (
            "复核失败/部分失败批次并归档错误报告。"
            if import_issue_rows
            else "保留导入批次作为关账底稿附件。"
        )

    checklist = [
        FinanceCloseChecklistItem(
            key="data_import_trace",
            name="数据导入追溯",
            owner="数据管理员",
            status=import_status,
            ready_count=import_ready_rows,
            issue_count=import_issue_rows,
            amount=0,
            description=import_description,
            next_step=import_next_step,
        ),
        FinanceCloseChecklistItem(
            key="revenue_confirmation",
            name="收入确认与收款时间",
            owner="门店会计",
            status=_readiness_status(
                missing_payment_count + open_order_count,
                missing_payment_amount + open_order_amount,
            ),
            ready_count=max(0, order_count - missing_payment_count - open_order_count),
            issue_count=missing_payment_count + open_order_count,
            amount=round(missing_payment_amount + open_order_amount, 2),
            description=(
                f"本期有效订单 {order_count} 笔，需处理未记录收款时间或未完结订单 "
                f"{missing_payment_count + open_order_count} 笔。"
            ),
            next_step="补齐收款时间，核对未完结订单是否应跨期或撤销。",
        ),
        FinanceCloseChecklistItem(
            key="expense_approval",
            name="费用审批与发票完整性",
            owner="费用会计",
            status=_readiness_status(
                pending_expense_count,
                pending_expense_amount,
                warning_only=expense_count == 0,
            ),
            ready_count=max(0, expense_count - pending_expense_count),
            issue_count=pending_expense_count,
            amount=round(pending_expense_amount, 2),
            description=(
                f"本期费用 {expense_count} 笔，待审批/被退回 {pending_expense_count} 笔，"
                f"发票号缺失 {missing_invoice_count} 笔。"
            ),
            next_step="先处理待审批费用，再按供应商补齐发票号和附件。",
        ),
        FinanceCloseChecklistItem(
            key="payment_cutoff",
            name="付款截止与应付清单",
            owner="出纳",
            status=_readiness_status(approved_unpaid_count, approved_unpaid_amount),
            ready_count=max(0, expense_count - approved_unpaid_count),
            issue_count=approved_unpaid_count,
            amount=round(approved_unpaid_amount, 2),
            description=(
                f"已审批未支付费用 {approved_unpaid_count} 笔，"
                f"金额 {approved_unpaid_amount:.2f} 元。"
            ),
            next_step="确认是否纳入本期应付，形成排款和银行付款清单。",
        ),
        FinanceCloseChecklistItem(
            key="budget_coverage",
            name="预算覆盖与执行复核",
            owner="预算负责人",
            status="ready" if budget_count else "warning",
            ready_count=budget_count,
            issue_count=0 if budget_count else 1,
            amount=0,
            description=(
                f"本期匹配到 {budget_count} 条预算记录。"
                if budget_count
                else "本期未匹配到预算记录，预算执行率无法完整复核。"
            ),
            next_step="补齐缺失月份或门店的预算底稿，标记超预算科目。",
        ),
        FinanceCloseChecklistItem(
            key="audit_trail",
            name="审计留痕",
            owner="系统管理员",
            status="ready" if audit_count else "warning",
            ready_count=audit_count,
            issue_count=0 if audit_count else 1,
            amount=0,
            description=f"本期审计日志 {audit_count} 条。",
            next_step="保留登录、查询、导入、导出和关键数据变更日志。",
        ),
    ]

    metrics = {
        "order_count": order_count,
        "order_amount": order_amount,
        "missing_payment_count": missing_payment_count,
        "missing_payment_amount": missing_payment_amount,
        "open_order_count": open_order_count,
        "open_order_amount": open_order_amount,
        "expense_count": expense_count,
        "expense_amount": expense_amount,
        "pending_expense_count": pending_expense_count,
        "pending_expense_amount": pending_expense_amount,
        "approved_unpaid_count": approved_unpaid_count,
        "approved_unpaid_amount": approved_unpaid_amount,
        "budget_count": budget_count,
        "audit_count": audit_count,
        "import_issue_count": import_issue_count,
    }
    return checklist, metrics


async def _bank_reconciliation_items(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> list[BankReconciliationItem]:
    order_conditions = [
        OrderHeader.biz_date >= start_date,
        OrderHeader.biz_date <= end_date,
        OrderHeader.status.notin_(["cancelled", "refunded"]),
    ]
    expense_conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date,
        ExpenseRecord.status.in_(["approved", "paid"]),
        ExpenseRecord.is_deleted.is_(False),
    ]
    if accessible_store_ids is not None:
        order_conditions.append(OrderHeader.store_id.in_(accessible_store_ids))
        expense_conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))

    order_channel = func.coalesce(OrderHeader.payment_method, "未记录")
    inflow_rows = (
        await db.execute(
            select(
                order_channel,
                func.sum(OrderHeader.net_amount),
                func.count(OrderHeader.id),
                func.sum(case((OrderHeader.payment_time.is_(None), 1), else_=0)),
                func.sum(
                    case(
                        (OrderHeader.payment_time.is_(None), OrderHeader.net_amount),
                        else_=0,
                    )
                ),
            )
            .where(*order_conditions)
            .group_by(order_channel)
        )
    ).all()

    expense_channel = func.coalesce(ExpenseRecord.payment_method, "未记录")
    outflow_issue = or_(
        ExpenseRecord.status != "paid",
        func.coalesce(ExpenseRecord.payment_account, "") == "",
        func.coalesce(ExpenseRecord.payment_method, "") == "",
    )
    outflow_rows = (
        await db.execute(
            select(
                expense_channel,
                func.sum(ExpenseRecord.amount),
                func.count(ExpenseRecord.id),
                func.sum(case((outflow_issue, 1), else_=0)),
                func.sum(case((outflow_issue, ExpenseRecord.amount), else_=0)),
            )
            .where(*expense_conditions)
            .group_by(expense_channel)
        )
    ).all()

    items: list[BankReconciliationItem] = []
    for channel, amount, count, unmatched_count, unmatched_amount in inflow_rows:
        issue_count = int(unmatched_count or 0)
        issue_amount = _to_float(unmatched_amount)
        items.append(
            BankReconciliationItem(
                channel=f"收款-{channel}",
                direction="inflow",
                expected_amount=round(_to_float(amount), 2),
                record_count=int(count or 0),
                unmatched_count=issue_count,
                unmatched_amount=round(issue_amount, 2),
                status=_readiness_status(issue_count, issue_amount),
                account_hint="以支付方式映射银行/第三方收款账户。",
            )
        )

    for channel, amount, count, unmatched_count, unmatched_amount in outflow_rows:
        issue_count = int(unmatched_count or 0)
        issue_amount = _to_float(unmatched_amount)
        items.append(
            BankReconciliationItem(
                channel=f"付款-{channel}",
                direction="outflow",
                expected_amount=round(_to_float(amount), 2),
                record_count=int(count or 0),
                unmatched_count=issue_count,
                unmatched_amount=round(issue_amount, 2),
                status=_readiness_status(issue_count, issue_amount),
                account_hint="核对支付账户、付款状态与银行付款流水。",
            )
        )

    status_order = {"blocker": 0, "warning": 1, "ready": 2}
    return sorted(
        items,
        key=lambda item: (status_order.get(item.status, 9), -item.unmatched_amount),
    )[:10]


def _ledger_readiness_items(
    checklist: list[FinanceCloseChecklistItem],
    metrics: dict[str, float | int],
) -> list[LedgerReadinessItem]:
    checklist_map = {item.key: item for item in checklist}
    revenue_issues = int(metrics["missing_payment_count"]) + int(
        metrics["open_order_count"]
    )
    expense_issues = int(metrics["pending_expense_count"]) + int(
        metrics["approved_unpaid_count"]
    )

    return [
        LedgerReadinessItem(
            key="revenue_workpaper",
            name="收入凭证底稿",
            status=checklist_map["revenue_confirmation"].status,
            coverage=_coverage(int(metrics["order_count"]), revenue_issues),
            source="order_header",
            remark="以订单净额、业务日期、支付方式和收款时间生成收入底稿。",
        ),
        LedgerReadinessItem(
            key="expense_workpaper",
            name="费用凭证底稿",
            status=checklist_map["expense_approval"].status
            if checklist_map["expense_approval"].status == "blocker"
            else checklist_map["payment_cutoff"].status,
            coverage=_coverage(int(metrics["expense_count"]), expense_issues),
            source="expense_record",
            remark="以费用科目、供应商、发票号、审批状态和付款状态生成费用底稿。",
        ),
        LedgerReadinessItem(
            key="budget_workpaper",
            name="预算执行底稿",
            status=checklist_map["budget_coverage"].status,
            coverage=100.0 if int(metrics["budget_count"]) else 0.0,
            source="budgets",
            remark="预算记录可支持本期实际、预算、差异和执行率复核。",
        ),
        LedgerReadinessItem(
            key="audit_workpaper",
            name="审计追溯底稿",
            status=checklist_map["audit_trail"].status,
            coverage=100.0 if int(metrics["audit_count"]) else 0.0,
            source="audit_log",
            remark="审计日志用于追溯导入、查询、导出和关键变更。",
        ),
        LedgerReadinessItem(
            key="general_ledger_model",
            name="总账模型",
            status="planned",
            coverage=35.0,
            source="planned",
            remark="下一步需要会计科目表、凭证分录、期间关账和反关账权限。",
        ),
    ]


def _close_actions(
    checklist: list[FinanceCloseChecklistItem],
    metrics: dict[str, float | int],
) -> list[FinanceActionItem]:
    actions: list[FinanceActionItem] = []
    if int(metrics["missing_payment_count"]) or int(metrics["open_order_count"]):
        actions.append(
            FinanceActionItem(
                priority="P0",
                title="处理收入确认与收款时间差异",
                owner="门店会计",
                reason=(
                    f"仍有 {int(metrics['missing_payment_count']) + int(metrics['open_order_count'])} "
                    f"笔订单影响收入底稿，金额 {float(metrics['missing_payment_amount']) + float(metrics['open_order_amount']):.2f} 元。"
                ),
                due_hint="关账前",
            )
        )
    if int(metrics["pending_expense_count"]):
        actions.append(
            FinanceActionItem(
                priority="P1",
                title="清理待审批或被退回费用",
                owner="费用会计",
                reason=(
                    f"待处理费用 {int(metrics['pending_expense_count'])} 笔，"
                    f"金额 {float(metrics['pending_expense_amount']):.2f} 元。"
                ),
                due_hint="2 个工作日内",
            )
        )
    if int(metrics["approved_unpaid_count"]):
        actions.append(
            FinanceActionItem(
                priority="P1",
                title="确认已审批未付款费用是否转应付",
                owner="出纳",
                reason=(
                    f"已审批未支付 {int(metrics['approved_unpaid_count'])} 笔，"
                    f"金额 {float(metrics['approved_unpaid_amount']):.2f} 元。"
                ),
                due_hint="关账检查会前",
            )
        )
    if not int(metrics["budget_count"]):
        actions.append(
            FinanceActionItem(
                priority="P2",
                title="补齐本期预算底稿",
                owner="预算负责人",
                reason="缺少预算记录会削弱费用差异分析和超预算复核。",
                due_hint="本周内",
            )
        )
    if not int(metrics["audit_count"]):
        actions.append(
            FinanceActionItem(
                priority="P2",
                title="复核审计日志采集链路",
                owner="系统管理员",
                reason="本期没有审计日志，无法完整追溯关账前关键操作。",
                due_hint="本周内",
            )
        )

    blockers = [item for item in checklist if item.status == "blocker"]
    if not actions and not blockers:
        actions.append(
            FinanceActionItem(
                priority="P2",
                title="进入总账与期间关账建模",
                owner="财务信息化负责人",
                reason="现有经营数据已能支撑关账前检查，下一阶段可设计科目、凭证和期间状态。",
                due_hint="下阶段迭代",
            )
        )
    return actions[:6]


async def get_finance_close_readiness(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
) -> FinanceCloseReadinessOverview:
    """Build a period-close readiness view from current operational data."""

    checklist, metrics = await _close_checklist(
        db, start_date, end_date, accessible_store_ids
    )
    bank_items = await _bank_reconciliation_items(
        db, start_date, end_date, accessible_store_ids
    )
    ledger_items = _ledger_readiness_items(checklist, metrics)

    checklist_score_map = {"ready": 100, "warning": 72, "blocker": 42, "planned": 35}
    checklist_score = sum(
        checklist_score_map.get(item.status, 50) for item in checklist
    ) / max(len(checklist), 1)
    ledger_score = sum(
        item.coverage for item in ledger_items if item.key != "general_ledger_model"
    ) / max(len([item for item in ledger_items if item.key != "general_ledger_model"]), 1)
    close_score = int(round(checklist_score * 0.45 + ledger_score * 0.55))

    return FinanceCloseReadinessOverview(
        generated_at=datetime.now(tz=UTC),
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        close_score=max(0, min(100, close_score)),
        checklist=checklist,
        bank_reconciliation=bank_items,
        ledger_readiness=ledger_items,
        action_items=_close_actions(checklist, metrics),
    )


def _period_label(start_date: date, end_date: date) -> str:
    if start_date.year == end_date.year and start_date.month == end_date.month:
        return f"{start_date.year}-{start_date.month:02d}"
    return f"{start_date.isoformat()}~{end_date.isoformat()}"


def _status_from_issues(issue_count: int, *, planned: bool = False) -> str:
    if planned:
        return "planned"
    if issue_count >= 5:
        return "warning"
    if issue_count > 0:
        return "partial"
    return "ready"


def _finance_suite_accounts() -> list[ChartOfAccountItem]:
    return [
        ChartOfAccountItem(
            code="1002",
            name="银行存款",
            category="asset",
            balance_direction="debit",
            mapped_source="支付方式/支付账户",
            status="partial",
        ),
        ChartOfAccountItem(
            code="1122",
            name="应收账款",
            category="asset",
            balance_direction="debit",
            mapped_source="未完结订单、未记录收款时间订单",
            status="partial",
        ),
        ChartOfAccountItem(
            code="2202",
            name="应付账款",
            category="liability",
            balance_direction="credit",
            mapped_source="已提交/已审批费用",
            status="partial",
        ),
        ChartOfAccountItem(
            code="5001",
            name="主营业务收入",
            category="revenue",
            balance_direction="credit",
            mapped_source="订单净额",
            status="ready",
        ),
        ChartOfAccountItem(
            code="6601",
            name="销售费用",
            category="expense",
            balance_direction="debit",
            mapped_source="费用科目",
            status="ready",
        ),
        ChartOfAccountItem(
            code="1601",
            name="固定资产",
            category="asset",
            balance_direction="debit",
            mapped_source="资产类费用线索",
            status="partial",
        ),
        ChartOfAccountItem(
            code="2221",
            name="应交税费",
            category="liability",
            balance_direction="credit",
            mapped_source="销项/进项税额测算",
            status="partial",
        ),
    ]


async def _finance_suite_base_metrics(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> dict[str, float | int]:
    order_conditions = [
        OrderHeader.biz_date >= start_date,
        OrderHeader.biz_date <= end_date,
        OrderHeader.status.notin_(["cancelled", "refunded"]),
    ]
    expense_conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date,
        ExpenseRecord.is_deleted.is_(False),
    ]
    if accessible_store_ids is not None:
        order_conditions.append(OrderHeader.store_id.in_(accessible_store_ids))
        expense_conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))

    order_row = (
        await db.execute(
            select(
                func.count(OrderHeader.id),
                func.sum(OrderHeader.net_amount),
                func.sum(case((OrderHeader.payment_time.is_(None), 1), else_=0)),
                func.sum(
                    case(
                        (OrderHeader.payment_time.is_(None), OrderHeader.net_amount),
                        else_=0,
                    )
                ),
            ).where(*order_conditions)
        )
    ).one()

    expense_row = (
        await db.execute(
            select(
                func.count(ExpenseRecord.id),
                func.sum(ExpenseRecord.amount),
                func.sum(
                    case(
                        (
                            ExpenseRecord.status.in_(
                                ["draft", "submitted", "rejected"]
                            ),
                            1,
                        ),
                        else_=0,
                    )
                ),
                func.sum(
                    case(
                        (ExpenseRecord.status == "approved", ExpenseRecord.amount),
                        else_=0,
                    )
                ),
                func.sum(
                    case(
                        (
                            func.coalesce(ExpenseRecord.invoice_no, "") == "",
                            1,
                        ),
                        else_=0,
                    )
                ),
            ).where(*expense_conditions)
        )
    ).one()

    budget_conditions = [
        (Budget.year * 100 + Budget.month) >= start_date.year * 100 + start_date.month,
        (Budget.year * 100 + Budget.month) <= end_date.year * 100 + end_date.month,
    ]
    if accessible_store_ids is not None:
        budget_conditions.append(Budget.store_id.in_(accessible_store_ids))
    budget_total = _to_float(
        (await db.execute(select(func.sum(Budget.amount)).where(*budget_conditions))).scalar()
    )

    return {
        "order_count": int(order_row[0] or 0),
        "revenue_amount": _to_float(order_row[1]),
        "missing_payment_count": int(order_row[2] or 0),
        "missing_payment_amount": _to_float(order_row[3]),
        "expense_count": int(expense_row[0] or 0),
        "expense_amount": _to_float(expense_row[1]),
        "pending_expense_count": int(expense_row[2] or 0),
        "approved_unpaid_amount": _to_float(expense_row[3]),
        "missing_invoice_count": int(expense_row[4] or 0),
        "budget_amount": budget_total,
    }


async def _finance_suite_bank_accounts(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> list[BankAccountItem]:
    reconciliation = await _bank_reconciliation_items(
        db, start_date, end_date, accessible_store_ids
    )
    return [
        BankAccountItem(
            name=item.channel,
            channel=item.channel.replace("收款-", "").replace("付款-", ""),
            direction=item.direction,
            statement_amount=item.expected_amount,
            matched_amount=round(item.expected_amount - item.unmatched_amount, 2),
            unmatched_amount=item.unmatched_amount,
            unmatched_count=item.unmatched_count,
            status=item.status,
        )
        for item in reconciliation
    ]


async def _finance_suite_counterparties(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> list[CounterpartyLedgerItem]:
    order_conditions = [
        OrderHeader.biz_date >= start_date,
        OrderHeader.biz_date <= end_date,
        OrderHeader.status.notin_(["cancelled", "refunded"]),
        or_(OrderHeader.status != "completed", OrderHeader.payment_time.is_(None)),
    ]
    expense_conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date,
        ExpenseRecord.status.in_(["submitted", "approved"]),
        ExpenseRecord.is_deleted.is_(False),
    ]
    if accessible_store_ids is not None:
        order_conditions.append(OrderHeader.store_id.in_(accessible_store_ids))
        expense_conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))

    order_counterparty = func.coalesce(OrderHeader.channel, "未记录渠道")
    receivable_rows = (
        await db.execute(
            select(
                order_counterparty,
                func.sum(OrderHeader.net_amount),
                func.count(OrderHeader.id),
            )
            .where(*order_conditions)
            .group_by(order_counterparty)
            .order_by(desc(func.sum(OrderHeader.net_amount)))
            .limit(8)
        )
    ).all()

    expense_counterparty = func.coalesce(ExpenseRecord.vendor, "未维护供应商")
    payable_rows = (
        await db.execute(
            select(
                expense_counterparty,
                func.sum(ExpenseRecord.amount),
                func.count(ExpenseRecord.id),
            )
            .where(*expense_conditions)
            .group_by(expense_counterparty)
            .order_by(desc(func.sum(ExpenseRecord.amount)))
            .limit(8)
        )
    ).all()

    items: list[CounterpartyLedgerItem] = []
    for counterparty, amount, count in receivable_rows:
        open_amount = _to_float(amount)
        items.append(
            CounterpartyLedgerItem(
                counterparty=f"销售渠道-{counterparty}",
                ledger_type="receivable",
                amount=round(open_amount, 2),
                record_count=int(count or 0),
                aging_bucket="0-30天",
                status="overdue" if open_amount > 100000 else "watch",
                next_step="核对平台/门店收款流水并完成收入核销。",
            )
        )
    for counterparty, amount, count in payable_rows:
        open_amount = _to_float(amount)
        items.append(
            CounterpartyLedgerItem(
                counterparty=counterparty,
                ledger_type="payable",
                amount=round(open_amount, 2),
                record_count=int(count or 0),
                aging_bucket="本期待付款",
                status="overdue" if open_amount > 100000 else "watch",
                next_step="确认付款计划、发票状态和应付入账期间。",
            )
        )
    return sorted(items, key=lambda item: item.amount, reverse=True)[:12]


async def _finance_suite_budget_versions(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> list[BudgetVersionItem]:
    controls = await _budget_controls(db, start_date, end_date, accessible_store_ids)
    rows: list[BudgetVersionItem] = []
    for item in controls[:10]:
        approval_status = "required" if item.status == "over" else "normal"
        if item.status == "watch":
            approval_status = "pending"
        rows.append(
            BudgetVersionItem(
                version_name=f"{_period_label(start_date, end_date)}滚动预算",
                scope=item.name,
                budget_amount=item.budget,
                actual_amount=item.actual,
                variance_amount=item.variance,
                approval_status=approval_status,
                owner="预算负责人",
            )
        )
    if not rows:
        rows.append(
            BudgetVersionItem(
                version_name=f"{_period_label(start_date, end_date)}预算版本",
                scope="全部门店/全部科目",
                budget_amount=0,
                actual_amount=0,
                variance_amount=0,
                approval_status="required",
                owner="预算负责人",
            )
        )
    return rows


async def _finance_suite_fixed_assets(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> list[FixedAssetItem]:
    conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date,
        ExpenseRecord.is_deleted.is_(False),
        or_(
            ExpenseType.name.ilike("%设备%"),
            ExpenseType.name.ilike("%装修%"),
            ExpenseType.name.ilike("%资产%"),
            ExpenseType.name.ilike("%维修%"),
            ExpenseRecord.description.ilike("%设备%"),
            ExpenseRecord.description.ilike("%装修%"),
            ExpenseRecord.description.ilike("%资产%"),
        ),
    ]
    if accessible_store_ids is not None:
        conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))

    rows = (
        await db.execute(
            select(
                Store.name,
                ExpenseType.name,
                func.sum(ExpenseRecord.amount),
                func.count(ExpenseRecord.id),
            )
            .select_from(ExpenseRecord)
            .join(ExpenseType, ExpenseRecord.expense_type_id == ExpenseType.id)
            .join(Store, ExpenseRecord.store_id == Store.id)
            .where(*conditions)
            .group_by(Store.name, ExpenseType.name)
            .order_by(desc(func.sum(ExpenseRecord.amount)))
            .limit(8)
        )
    ).all()

    assets: list[FixedAssetItem] = []
    for store_name, category, amount, count in rows:
        original_value = _to_float(amount)
        monthly_depreciation = round(original_value / 36, 2) if original_value else 0.0
        assets.append(
            FixedAssetItem(
                asset_name=f"{store_name}-{category}资产包",
                store_name=store_name,
                category=category,
                original_value=round(original_value, 2),
                monthly_depreciation=monthly_depreciation,
                net_value=round(max(original_value - monthly_depreciation, 0), 2),
                status="checking" if count else "planned",
            )
        )
    if not assets:
        assets.append(
            FixedAssetItem(
                asset_name="固定资产卡片模板",
                store_name="全部门店",
                category="待建档",
                original_value=0,
                monthly_depreciation=0,
                net_value=0,
                status="planned",
            )
        )
    return assets


async def _finance_suite_tax_invoices(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
    metrics: dict[str, float | int],
) -> list[TaxInvoiceItem]:
    expense_conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date,
        ExpenseRecord.is_deleted.is_(False),
    ]
    if accessible_store_ids is not None:
        expense_conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))

    invoice_row = (
        await db.execute(
            select(
                func.count(ExpenseRecord.id),
                func.sum(ExpenseRecord.amount),
                func.sum(
                    case(
                        (
                            func.coalesce(ExpenseRecord.invoice_no, "") == "",
                            1,
                        ),
                        else_=0,
                    )
                ),
            ).where(*expense_conditions)
        )
    ).one()

    revenue_amount = float(metrics["revenue_amount"])
    expense_amount = _to_float(invoice_row[1])
    missing_invoice_count = int(invoice_row[2] or 0)
    invoice_count = int(invoice_row[0] or 0) - missing_invoice_count
    return [
        TaxInvoiceItem(
            invoice_type="output",
            source="订单收入销项税测算",
            taxable_amount=round(revenue_amount, 2),
            tax_rate=6.0,
            tax_amount=round(revenue_amount * 0.06, 2),
            invoice_count=int(metrics["order_count"]),
            missing_invoice_count=0,
            status="ready" if revenue_amount else "warning",
        ),
        TaxInvoiceItem(
            invoice_type="input",
            source="费用进项票据台账",
            taxable_amount=round(expense_amount, 2),
            tax_rate=6.0,
            tax_amount=round(expense_amount * 0.06, 2),
            invoice_count=max(invoice_count, 0),
            missing_invoice_count=missing_invoice_count,
            status="warning" if missing_invoice_count else "ready",
        ),
    ]


async def _finance_suite_close_consolidation(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None,
) -> list[CloseConsolidationItem]:
    store_conditions = []
    if accessible_store_ids is not None:
        store_conditions.append(Store.id.in_(accessible_store_ids))

    stores = (
        await db.execute(
            select(Store.id, Store.name).where(*store_conditions).order_by(Store.id).limit(8)
        )
    ).all()
    rows: list[CloseConsolidationItem] = []
    total_revenue = 0.0
    total_expense = 0.0
    total_blockers = 0
    for store_id, store_name in stores:
        revenue = _to_float(
            (
                await db.execute(
                    select(func.sum(OrderHeader.net_amount))
                    .where(OrderHeader.biz_date >= start_date)
                    .where(OrderHeader.biz_date <= end_date)
                    .where(OrderHeader.store_id == store_id)
                    .where(OrderHeader.status.notin_(["cancelled", "refunded"]))
                )
            ).scalar()
        )
        expense = _to_float(
            (
                await db.execute(
                    select(func.sum(ExpenseRecord.amount))
                    .where(ExpenseRecord.biz_date >= start_date)
                    .where(ExpenseRecord.biz_date <= end_date)
                    .where(ExpenseRecord.store_id == store_id)
                    .where(ExpenseRecord.is_deleted.is_(False))
                )
            ).scalar()
        )
        blockers = int(
            (
                await db.execute(
                    select(func.count(OrderHeader.id))
                    .where(OrderHeader.biz_date >= start_date)
                    .where(OrderHeader.biz_date <= end_date)
                    .where(OrderHeader.store_id == store_id)
                    .where(OrderHeader.status.notin_(["cancelled", "refunded"]))
                    .where(OrderHeader.payment_time.is_(None))
                )
            ).scalar()
            or 0
        )
        total_revenue += revenue
        total_expense += expense
        total_blockers += blockers
        rows.append(
            CloseConsolidationItem(
                store_name=store_name,
                revenue_amount=round(revenue, 2),
                expense_amount=round(expense, 2),
                profit_amount=round(revenue - expense, 2),
                close_status="ready" if blockers == 0 else "checking",
                blocker_count=blockers,
                consolidation_note="可纳入合并" if blockers == 0 else "需先完成收款时间核对",
            )
        )
    rows.insert(
        0,
        CloseConsolidationItem(
            store_name="合并口径",
            revenue_amount=round(total_revenue, 2),
            expense_amount=round(total_expense, 2),
            profit_amount=round(total_revenue - total_expense, 2),
            close_status="ready" if total_blockers == 0 else "checking",
            blocker_count=total_blockers,
            consolidation_note="多门店合并预览，暂不生成正式合并抵消分录。",
        ),
    )
    return rows


def _finance_suite_journal_previews(
    start_date: date,
    end_date: date,
    metrics: dict[str, float | int],
) -> list[JournalEntryPreviewItem]:
    entry_date = end_date.isoformat()
    revenue = float(metrics["revenue_amount"])
    expense = float(metrics["expense_amount"])
    missing_payment = float(metrics["missing_payment_amount"])
    approved_unpaid = float(metrics["approved_unpaid_amount"])
    return [
        JournalEntryPreviewItem(
            source_type="orders",
            entry_date=entry_date,
            summary=f"{_period_label(start_date, end_date)}营业收入确认",
            debit_account="1002 银行存款/1122 应收账款",
            credit_account="5001 主营业务收入",
            amount=round(revenue, 2),
            status="blocked" if missing_payment else "ready",
        ),
        JournalEntryPreviewItem(
            source_type="expenses",
            entry_date=entry_date,
            summary=f"{_period_label(start_date, end_date)}经营费用归集",
            debit_account="6601 销售费用",
            credit_account="1002 银行存款/2202 应付账款",
            amount=round(expense, 2),
            status="blocked" if int(metrics["pending_expense_count"]) else "ready",
        ),
        JournalEntryPreviewItem(
            source_type="payables",
            entry_date=entry_date,
            summary="已审批未付款费用转应付",
            debit_account="6601 销售费用",
            credit_account="2202 应付账款",
            amount=round(approved_unpaid, 2),
            status="preview" if approved_unpaid else "ready",
        ),
        JournalEntryPreviewItem(
            source_type="tax",
            entry_date=entry_date,
            summary="销项税额测算",
            debit_account="5001 主营业务收入",
            credit_account="2221 应交税费",
            amount=round(revenue * 0.06, 2),
            status="preview",
        ),
    ]


def _finance_suite_modules(
    metrics: dict[str, float | int],
    bank_accounts: list[BankAccountItem],
    counterparties: list[CounterpartyLedgerItem],
    budget_versions: list[BudgetVersionItem],
    fixed_assets: list[FixedAssetItem],
    tax_invoices: list[TaxInvoiceItem],
    close_rows: list[CloseConsolidationItem],
) -> list[FinanceSuiteModule]:
    bank_issues = sum(item.unmatched_count for item in bank_accounts)
    arap_issues = len([item for item in counterparties if item.status != "normal"])
    budget_issues = len(
        [item for item in budget_versions if item.approval_status != "normal"]
    )
    asset_issues = len([item for item in fixed_assets if item.status != "active"])
    tax_issues = sum(item.missing_invoice_count for item in tax_invoices)
    close_issues = close_rows[0].blocker_count if close_rows else 0
    journal_issues = int(metrics["missing_payment_count"]) + int(
        metrics["pending_expense_count"]
    )

    return [
        FinanceSuiteModule(
            key="general_ledger",
            name="总账与会计期间",
            priority="P0",
            status=_status_from_issues(journal_issues),
            maturity_score=72 if journal_issues == 0 else 58,
            metric_label="凭证预览金额",
            metric_value=round(float(metrics["revenue_amount"]) + float(metrics["expense_amount"]), 2),
            issue_count=journal_issues,
            description="已建立科目映射和经营数据凭证预览，正式过账仍需凭证表与期间锁定。",
        ),
        FinanceSuiteModule(
            key="bank_reconciliation",
            name="银行流水与对账",
            priority="P0",
            status=_status_from_issues(bank_issues),
            maturity_score=78 if bank_issues == 0 else 63,
            metric_label="未匹配金额",
            metric_value=round(sum(item.unmatched_amount for item in bank_accounts), 2),
            issue_count=bank_issues,
            description="按收付款通道生成对账账户视图，支持后续接入真实银行流水。",
        ),
        FinanceSuiteModule(
            key="receivable_payable",
            name="应收应付台账",
            priority="P1",
            status=_status_from_issues(arap_issues),
            maturity_score=76 if arap_issues == 0 else 66,
            metric_label="往来未结金额",
            metric_value=round(sum(item.amount for item in counterparties), 2),
            issue_count=arap_issues,
            description="从未完结订单和待付款费用生成客户/供应商往来台账。",
        ),
        FinanceSuiteModule(
            key="budget_workflow",
            name="预算版本与超预算审批",
            priority="P1",
            status=_status_from_issues(budget_issues),
            maturity_score=82 if budget_issues == 0 else 70,
            metric_label="待审批版本",
            metric_value=budget_issues,
            issue_count=budget_issues,
            description="按费用科目形成滚动预算版本，并标记超预算审批需求。",
        ),
        FinanceSuiteModule(
            key="fixed_assets",
            name="固定资产",
            priority="P1",
            status=_status_from_issues(asset_issues),
            maturity_score=68 if asset_issues == 0 else 56,
            metric_label="资产净值",
            metric_value=round(sum(item.net_value for item in fixed_assets), 2),
            issue_count=asset_issues,
            description="从设备、装修、资产类费用提取资产卡片线索并测算折旧。",
        ),
        FinanceSuiteModule(
            key="tax_invoice",
            name="税务与发票",
            priority="P2",
            status=_status_from_issues(tax_issues),
            maturity_score=74 if tax_issues == 0 else 60,
            metric_label="缺票记录",
            metric_value=tax_issues,
            issue_count=tax_issues,
            description="生成销项/进项税额测算和发票完整性台账。",
        ),
        FinanceSuiteModule(
            key="close_consolidation",
            name="财务关账与合并",
            priority="P2",
            status=_status_from_issues(close_issues),
            maturity_score=80 if close_issues == 0 else 62,
            metric_label="合并阻断项",
            metric_value=close_issues,
            issue_count=close_issues,
            description="按门店形成关账状态和合并口径预览，暂不生成抵消分录。",
        ),
    ]


def _finance_suite_actions(
    modules: list[FinanceSuiteModule],
    metrics: dict[str, float | int],
) -> list[FinanceActionItem]:
    actions: list[FinanceActionItem] = []
    for module in modules:
        if module.issue_count <= 0:
            continue
        priority = "P0" if module.priority == "P0" else "P1"
        actions.append(
            FinanceActionItem(
                priority=priority,
                title=f"推进{module.name}问题清理",
                owner="财务负责人",
                reason=f"{module.name}仍有 {module.issue_count} 个待处理项，影响模块成熟度。",
                due_hint="本期关账前",
            )
        )
    if int(metrics["missing_invoice_count"]):
        actions.append(
            FinanceActionItem(
                priority="P1",
                title="补齐费用发票台账",
                owner="费用会计",
                reason=f"费用记录中仍有 {int(metrics['missing_invoice_count'])} 条缺少发票号。",
                due_hint="3 个工作日内",
            )
        )
    if not actions:
        actions.append(
            FinanceActionItem(
                priority="P2",
                title="将预览能力升级为正式核算引擎",
                owner="财务信息化负责人",
                reason="剩余模块已具备数据视图，下一步可补充正式凭证、期间锁定和审批流状态表。",
                due_hint="下阶段迭代",
            )
        )
    return actions[:8]


async def get_finance_suite_overview(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
) -> FinanceSuiteOverview:
    """Build the all-in-one finance suite for the remaining roadmap modules."""

    metrics = await _finance_suite_base_metrics(
        db, start_date, end_date, accessible_store_ids
    )
    period = GeneralLedgerPeriodItem(
        period=_period_label(start_date, end_date),
        status="checking"
        if int(metrics["missing_payment_count"]) or int(metrics["pending_expense_count"])
        else "open",
        revenue_amount=round(float(metrics["revenue_amount"]), 2),
        expense_amount=round(float(metrics["expense_amount"]), 2),
        journal_preview_count=4,
        unposted_count=int(metrics["missing_payment_count"])
        + int(metrics["pending_expense_count"]),
        next_step="处理阻断项后生成正式凭证与期间锁定记录。",
    )

    bank_accounts = await _finance_suite_bank_accounts(
        db, start_date, end_date, accessible_store_ids
    )
    counterparties = await _finance_suite_counterparties(
        db, start_date, end_date, accessible_store_ids
    )
    budget_versions = await _finance_suite_budget_versions(
        db, start_date, end_date, accessible_store_ids
    )
    fixed_assets = await _finance_suite_fixed_assets(
        db, start_date, end_date, accessible_store_ids
    )
    tax_invoices = await _finance_suite_tax_invoices(
        db, start_date, end_date, accessible_store_ids, metrics
    )
    close_rows = await _finance_suite_close_consolidation(
        db, start_date, end_date, accessible_store_ids
    )
    modules = _finance_suite_modules(
        metrics,
        bank_accounts,
        counterparties,
        budget_versions,
        fixed_assets,
        tax_invoices,
        close_rows,
    )

    return FinanceSuiteOverview(
        generated_at=datetime.now(tz=UTC),
        period_start=start_date.isoformat(),
        period_end=end_date.isoformat(),
        modules=modules,
        general_ledger_periods=[period],
        chart_of_accounts=_finance_suite_accounts(),
        journal_entry_previews=_finance_suite_journal_previews(
            start_date, end_date, metrics
        ),
        bank_accounts=bank_accounts,
        counterparty_ledgers=counterparties,
        budget_versions=budget_versions,
        fixed_assets=fixed_assets,
        tax_invoices=tax_invoices,
        close_consolidation=close_rows,
        action_items=_finance_suite_actions(modules, metrics),
    )
