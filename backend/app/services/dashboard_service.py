"""
Dashboard 仪表盘服务

提供管理驾驶舱所需的聚合数据，一次查询返回全部数据以减少前端请求。
所有聚合计算在数据库端完成。
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from dateutil.relativedelta import relativedelta
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import ExpenseRecord, ExpenseType
from app.models.kpi import KpiDailyStore
from app.models.store import Store
from app.schemas.dashboard import (
    SummaryCard,
    TrendDataPoint,
    StoreRankItem,
    ExpenseStructureItem,
    ChannelDistribution,
    DashboardOverview,
)


def _to_float(val: Any) -> float:
    """安全地将 Decimal/None 转为 float"""
    if val is None:
        return 0.0
    if isinstance(val, Decimal):
        return float(val)
    return float(val)


def _calc_growth_rate(current: float, previous: float) -> float | None:
    """计算增长率(%), previous 为 0 时返回 None"""
    if previous == 0:
        return None
    return round((current - previous) / abs(previous) * 100, 2)


def _kpi_base_filter(
    query: Any,
    start: date,
    end: date,
    accessible_store_ids: list[int] | None = None,
) -> Any:
    """为 KpiDailyStore 查询添加日期和门店过滤"""
    query = query.where(KpiDailyStore.biz_date >= start)
    query = query.where(KpiDailyStore.biz_date <= end)
    if accessible_store_ids is not None:
        query = query.where(KpiDailyStore.store_id.in_(accessible_store_ids))
    return query


async def _aggregate_kpi(
    db: AsyncSession,
    start: date,
    end: date,
    accessible_store_ids: list[int] | None = None,
) -> dict[str, float]:
    """对 kpi_daily_store 进行汇总聚合"""
    query = select(
        func.sum(KpiDailyStore.revenue),
        func.sum(KpiDailyStore.net_revenue),
        func.sum(KpiDailyStore.cost_total),
        func.sum(KpiDailyStore.operating_profit),
        func.sum(KpiDailyStore.order_count),
    ).select_from(KpiDailyStore)
    query = _kpi_base_filter(query, start, end, accessible_store_ids)

    result = await db.execute(query)
    row = result.one()

    revenue = _to_float(row[0])
    net_revenue = _to_float(row[1])
    cost_total = _to_float(row[2])
    operating_profit = _to_float(row[3])
    order_count = _to_float(row[4])

    avg_order_value = round(net_revenue / order_count, 2) if order_count > 0 else 0.0
    profit_rate = round(operating_profit / net_revenue * 100, 2) if net_revenue > 0 else 0.0

    return {
        "revenue": revenue,
        "net_revenue": net_revenue,
        "cost_total": cost_total,
        "operating_profit": operating_profit,
        "order_count": order_count,
        "avg_order_value": avg_order_value,
        "profit_rate": profit_rate,
    }


async def get_dashboard_overview(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
) -> DashboardOverview:
    """
    获取仪表盘全量数据

    一次调用返回: 核心指标卡片(含同比/环比) + 趋势 + 门店排名 + 费用结构 + 渠道分布 + 利润率仪表盘
    """
    # ── 1. 核心指标卡片(当期 + 同比 + 环比) ──
    period_days = (end_date - start_date).days + 1

    # 同比期(去年同期)
    yoy_start = start_date - relativedelta(years=1)
    yoy_end = end_date - relativedelta(years=1)

    # 环比期(上一等长时段)
    mom_start = start_date - timedelta(days=period_days)
    mom_end = start_date - timedelta(days=1)

    current = await _aggregate_kpi(db, start_date, end_date, accessible_store_ids)
    yoy = await _aggregate_kpi(db, yoy_start, yoy_end, accessible_store_ids)
    mom = await _aggregate_kpi(db, mom_start, mom_end, accessible_store_ids)

    # 活跃门店数
    store_count_q = select(func.count(Store.id)).where(Store.is_active.is_(True))
    if accessible_store_ids is not None:
        store_count_q = store_count_q.where(Store.id.in_(accessible_store_ids))
    store_count_result = await db.execute(store_count_q)
    active_store_count = store_count_result.scalar() or 0

    summary_cards: list[SummaryCard] = [
        SummaryCard(
            label="营业收入",
            value=round(current["revenue"], 2),
            unit="元",
            yoy_growth=_calc_growth_rate(current["revenue"], yoy["revenue"]),
            mom_growth=_calc_growth_rate(current["revenue"], mom["revenue"]),
        ),
        SummaryCard(
            label="营业利润",
            value=round(current["operating_profit"], 2),
            unit="元",
            yoy_growth=_calc_growth_rate(current["operating_profit"], yoy["operating_profit"]),
            mom_growth=_calc_growth_rate(current["operating_profit"], mom["operating_profit"]),
        ),
        SummaryCard(
            label="订单总数",
            value=current["order_count"],
            unit="笔",
            yoy_growth=_calc_growth_rate(current["order_count"], yoy["order_count"]),
            mom_growth=_calc_growth_rate(current["order_count"], mom["order_count"]),
        ),
        SummaryCard(
            label="客单价",
            value=round(current["avg_order_value"], 2),
            unit="元",
            yoy_growth=_calc_growth_rate(current["avg_order_value"], yoy["avg_order_value"]),
            mom_growth=_calc_growth_rate(current["avg_order_value"], mom["avg_order_value"]),
        ),
        SummaryCard(
            label="利润率",
            value=round(current["profit_rate"], 2),
            unit="%",
            # 利润率增长用百分点变动
            yoy_growth=round(current["profit_rate"] - yoy["profit_rate"], 2) if yoy["profit_rate"] != 0 else None,
            mom_growth=round(current["profit_rate"] - mom["profit_rate"], 2) if mom["profit_rate"] != 0 else None,
        ),
        SummaryCard(
            label="门店数",
            value=float(active_store_count),
            unit="家",
            yoy_growth=None,
            mom_growth=None,
        ),
    ]

    # ── 2. 营收趋势(查询期间) ──
    trend_query = (
        select(
            KpiDailyStore.biz_date,
            func.sum(KpiDailyStore.revenue),
            func.sum(KpiDailyStore.cost_total),
            func.sum(KpiDailyStore.operating_profit),
        )
        .select_from(KpiDailyStore)
        .group_by(KpiDailyStore.biz_date)
        .order_by(KpiDailyStore.biz_date)
    )
    trend_query = _kpi_base_filter(trend_query, start_date, end_date, accessible_store_ids)
    trend_result = await db.execute(trend_query)

    revenue_trend: list[TrendDataPoint] = [
        TrendDataPoint(
            date=str(row[0]),
            revenue=_to_float(row[1]),
            cost=_to_float(row[2]),
            profit=_to_float(row[3]),
        )
        for row in trend_result.all()
    ]

    # ── 3. 门店排名 TOP 5 ──
    rank_query = (
        select(
            Store.name,
            func.sum(KpiDailyStore.revenue).label("revenue"),
            func.sum(KpiDailyStore.operating_profit).label("profit"),
        )
        .select_from(KpiDailyStore)
        .join(Store, KpiDailyStore.store_id == Store.id)
        .group_by(Store.name)
        .order_by(desc("revenue"))
        .limit(5)
    )
    rank_query = _kpi_base_filter(rank_query, start_date, end_date, accessible_store_ids)
    rank_result = await db.execute(rank_query)

    store_ranking: list[StoreRankItem] = [
        StoreRankItem(
            store_name=row[0],
            revenue=_to_float(row[1]),
            profit=_to_float(row[2]),
        )
        for row in rank_result.all()
    ]

    # ── 4. 费用结构 ──
    expense_query = (
        select(
            ExpenseType.name,
            func.sum(ExpenseRecord.amount).label("total"),
        )
        .select_from(ExpenseRecord)
        .join(ExpenseType, ExpenseRecord.expense_type_id == ExpenseType.id)
        .where(ExpenseRecord.biz_date >= start_date)
        .where(ExpenseRecord.biz_date <= end_date)
        .where(ExpenseRecord.status == "approved")
        .group_by(ExpenseType.name)
        .order_by(desc("total"))
    )
    if accessible_store_ids is not None:
        expense_query = expense_query.where(
            ExpenseRecord.store_id.in_(accessible_store_ids)
        )
    expense_result = await db.execute(expense_query)

    expense_structure: list[ExpenseStructureItem] = [
        ExpenseStructureItem(name=row[0], value=_to_float(row[1]))
        for row in expense_result.all()
    ]

    # ── 5. 渠道分布 ──
    channel_query = select(
        func.sum(KpiDailyStore.dine_in_revenue),
        func.sum(KpiDailyStore.takeout_revenue),
        func.sum(KpiDailyStore.delivery_revenue),
        func.sum(KpiDailyStore.online_revenue),
    ).select_from(KpiDailyStore)
    channel_query = _kpi_base_filter(channel_query, start_date, end_date, accessible_store_ids)
    channel_result = await db.execute(channel_query)
    ch_row = channel_result.one()

    channel_distribution = ChannelDistribution(
        dine_in=_to_float(ch_row[0]),
        takeout=_to_float(ch_row[1]),
        delivery=_to_float(ch_row[2]),
        online=_to_float(ch_row[3]),
    )

    return DashboardOverview(
        summary_cards=summary_cards,
        revenue_trend=revenue_trend,
        store_ranking=store_ranking,
        expense_structure=expense_structure,
        channel_distribution=channel_distribution,
        profit_rate=round(current["profit_rate"], 2),
        profit_rate_target=15.0,
    )
