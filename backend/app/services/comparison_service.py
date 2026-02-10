"""
同比环比时间对比分析服务

提供期间对比汇总、趋势对比、门店对比等功能。
所有聚合计算在数据库端完成。
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from dateutil.relativedelta import relativedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.kpi import KpiDailyStore
from app.models.store import Store
from app.schemas.comparison import (
    MetricComparison,
    PeriodComparisonResponse,
    TrendComparisonItem,
    TrendComparisonResponse,
    StoreComparisonItem,
)


# ──────────────────── 工具函数 ────────────────────


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


def _resolve_compare_period(
    start_date: date,
    end_date: date,
    compare_type: str,
    compare_start_date: date | None = None,
    compare_end_date: date | None = None,
) -> tuple[date, date]:
    """
    根据对比类型推算对比期日期范围

    - yoy: 去年同期 (start_date - 1 year, end_date - 1 year)
    - mom: 上月同期 (start_date - 1 month, end_date - 1 month)
    - custom: 直接使用 compare_start_date / compare_end_date
    """
    if compare_type == "yoy":
        return (
            start_date - relativedelta(years=1),
            end_date - relativedelta(years=1),
        )
    elif compare_type == "mom":
        return (
            start_date - relativedelta(months=1),
            end_date - relativedelta(months=1),
        )
    else:  # custom
        if compare_start_date is None or compare_end_date is None:
            raise ValueError("自定义对比模式下必须提供 compare_start_date 和 compare_end_date")
        return compare_start_date, compare_end_date


def _format_period(start: date, end: date) -> str:
    """格式化期间显示文本"""
    return f"{start.isoformat()} ~ {end.isoformat()}"


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


# ──────────────── 指标定义 ────────────────

# (英文名, 中文名, SQL聚合列)
_METRIC_DEFS: list[tuple[str, str, Any]] = [
    ("revenue", "营业收入", func.sum(KpiDailyStore.revenue)),
    ("net_revenue", "净收入", func.sum(KpiDailyStore.net_revenue)),
    ("operating_profit", "营业利润", func.sum(KpiDailyStore.operating_profit)),
    ("cost_total", "总成本", func.sum(KpiDailyStore.cost_total)),
    ("order_count", "订单数", func.sum(KpiDailyStore.order_count)),
    ("customer_count", "客户数", func.sum(KpiDailyStore.customer_count)),
    ("avg_order_value", "客单价", None),  # 需要单独计算
]


async def _aggregate_period(
    db: AsyncSession,
    start: date,
    end: date,
    accessible_store_ids: list[int] | None = None,
) -> dict[str, float]:
    """对指定期间进行汇总聚合，返回各指标值的字典"""
    # 构造聚合列 (排除 avg_order_value，单独处理)
    agg_columns = [
        col for name, _, col in _METRIC_DEFS if col is not None
    ]
    query = select(*agg_columns)
    query = query.select_from(KpiDailyStore)
    query = _kpi_base_filter(query, start, end, accessible_store_ids)

    result = await db.execute(query)
    row = result.one()

    values: dict[str, float] = {}
    idx = 0
    for name, _, col in _METRIC_DEFS:
        if col is not None:
            values[name] = _to_float(row[idx])
            idx += 1

    # 计算客单价 = 净收入 / 订单数
    order_count = values.get("order_count", 0)
    if order_count > 0:
        values["avg_order_value"] = round(values.get("net_revenue", 0) / order_count, 2)
    else:
        values["avg_order_value"] = 0.0

    return values


# ──────────────── 核心服务函数 ────────────────


async def get_period_comparison(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    compare_type: str = "yoy",
    compare_start_date: date | None = None,
    compare_end_date: date | None = None,
    accessible_store_ids: list[int] | None = None,
) -> PeriodComparisonResponse:
    """
    期间对比汇总

    对比当期和对比期(同比/环比/自定义)的各项指标并计算增长率。
    """
    prev_start, prev_end = _resolve_compare_period(
        start_date, end_date, compare_type, compare_start_date, compare_end_date
    )

    # 并行聚合当期和对比期
    current_vals = await _aggregate_period(
        db, start_date, end_date, accessible_store_ids
    )
    previous_vals = await _aggregate_period(
        db, prev_start, prev_end, accessible_store_ids
    )

    # 构造指标对比列表
    metrics: list[MetricComparison] = []
    for name, label, _ in _METRIC_DEFS:
        cur = current_vals.get(name, 0.0)
        prev = previous_vals.get(name, 0.0)
        diff = round(cur - prev, 2)
        growth = _calc_growth_rate(cur, prev)
        metrics.append(
            MetricComparison(
                metric_name=name,
                metric_label=label,
                current_value=round(cur, 2),
                previous_value=round(prev, 2),
                difference=diff,
                growth_rate=growth,
            )
        )

    return PeriodComparisonResponse(
        current_period=_format_period(start_date, end_date),
        previous_period=_format_period(prev_start, prev_end),
        metrics=metrics,
    )


async def get_trend_comparison(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    metric: str = "revenue",
    compare_type: str = "yoy",
    compare_start_date: date | None = None,
    compare_end_date: date | None = None,
    accessible_store_ids: list[int] | None = None,
) -> TrendComparisonResponse:
    """
    趋势对比

    按日粒度返回当期和对比期指定指标的时间序列数据。
    两个期间按相对天偏移对齐。
    """
    prev_start, prev_end = _resolve_compare_period(
        start_date, end_date, compare_type, compare_start_date, compare_end_date
    )

    # 确定聚合列
    metric_label = metric
    metric_col: Any = None
    for name, label, col in _METRIC_DEFS:
        if name == metric:
            metric_label = label
            metric_col = col
            break

    if metric_col is None and metric == "avg_order_value":
        # 客单价需要 net_revenue 和 order_count
        pass
    elif metric_col is None:
        # 未知指标，默认使用 revenue
        metric = "revenue"
        metric_label = "营业收入"
        metric_col = func.sum(KpiDailyStore.revenue)

    # 查询当期每日数据
    current_data = await _query_daily_metric(
        db, start_date, end_date, metric, metric_col, accessible_store_ids
    )
    # 查询对比期每日数据
    previous_data = await _query_daily_metric(
        db, prev_start, prev_end, metric, metric_col, accessible_store_ids
    )

    # 按相对日偏移对齐
    current_days = (end_date - start_date).days + 1
    prev_days = (prev_end - prev_start).days + 1
    max_days = max(current_days, prev_days)

    items: list[TrendComparisonItem] = []
    for i in range(max_days):
        cur_date = start_date + timedelta(days=i)
        prev_date = prev_start + timedelta(days=i)

        date_label = cur_date.strftime("%m-%d") if i < current_days else prev_date.strftime("%m-%d")
        cur_val = current_data.get(cur_date, 0.0) if i < current_days else 0.0
        prev_val = previous_data.get(prev_date, 0.0) if i < prev_days else 0.0

        items.append(
            TrendComparisonItem(
                date_label=date_label,
                current_value=round(cur_val, 2),
                previous_value=round(prev_val, 2),
            )
        )

    return TrendComparisonResponse(
        current_period=_format_period(start_date, end_date),
        previous_period=_format_period(prev_start, prev_end),
        metric_name=metric,
        metric_label=metric_label,
        data=items,
    )


async def _query_daily_metric(
    db: AsyncSession,
    start: date,
    end: date,
    metric: str,
    metric_col: Any,
    accessible_store_ids: list[int] | None = None,
) -> dict[date, float]:
    """查询某指标的按日汇总数据，返回 {date: value} 字典"""
    if metric == "avg_order_value":
        # 客单价 = SUM(net_revenue) / SUM(order_count)
        query = select(
            KpiDailyStore.biz_date,
            func.sum(KpiDailyStore.net_revenue),
            func.sum(KpiDailyStore.order_count),
        ).select_from(KpiDailyStore)
        query = _kpi_base_filter(query, start, end, accessible_store_ids)
        query = query.group_by(KpiDailyStore.biz_date).order_by(KpiDailyStore.biz_date)

        result = await db.execute(query)
        data: dict[date, float] = {}
        for row in result.all():
            biz_date = row[0]
            net_rev = _to_float(row[1])
            count = _to_float(row[2])
            data[biz_date] = round(net_rev / count, 2) if count > 0 else 0.0
        return data
    else:
        query = select(
            KpiDailyStore.biz_date,
            metric_col,
        ).select_from(KpiDailyStore)
        query = _kpi_base_filter(query, start, end, accessible_store_ids)
        query = query.group_by(KpiDailyStore.biz_date).order_by(KpiDailyStore.biz_date)

        result = await db.execute(query)
        return {row[0]: _to_float(row[1]) for row in result.all()}


async def get_store_comparison(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    compare_type: str = "yoy",
    compare_start_date: date | None = None,
    compare_end_date: date | None = None,
    accessible_store_ids: list[int] | None = None,
) -> list[StoreComparisonItem]:
    """
    门店对比分析

    按门店维度对比当期与对比期的营收、利润、订单数、客单价。
    """
    prev_start, prev_end = _resolve_compare_period(
        start_date, end_date, compare_type, compare_start_date, compare_end_date
    )

    # 当期按门店聚合
    current_query = (
        select(
            KpiDailyStore.store_id,
            func.sum(KpiDailyStore.revenue).label("revenue"),
            func.sum(KpiDailyStore.operating_profit).label("profit"),
            func.sum(KpiDailyStore.order_count).label("order_count"),
            func.sum(KpiDailyStore.net_revenue).label("net_revenue"),
        )
        .select_from(KpiDailyStore)
        .group_by(KpiDailyStore.store_id)
    )
    current_query = _kpi_base_filter(
        current_query, start_date, end_date, accessible_store_ids
    )
    current_result = await db.execute(current_query)
    current_map: dict[int, dict[str, float]] = {}
    for row in current_result.all():
        sid = row[0]
        rev = _to_float(row[1])
        profit = _to_float(row[2])
        oc = _to_float(row[3])
        nr = _to_float(row[4])
        current_map[sid] = {
            "revenue": rev,
            "profit": profit,
            "order_count": oc,
            "avg_order_value": round(nr / oc, 2) if oc > 0 else 0.0,
        }

    # 对比期按门店聚合
    prev_query = (
        select(
            KpiDailyStore.store_id,
            func.sum(KpiDailyStore.revenue).label("revenue"),
            func.sum(KpiDailyStore.operating_profit).label("profit"),
            func.sum(KpiDailyStore.order_count).label("order_count"),
            func.sum(KpiDailyStore.net_revenue).label("net_revenue"),
        )
        .select_from(KpiDailyStore)
        .group_by(KpiDailyStore.store_id)
    )
    prev_query = _kpi_base_filter(prev_query, prev_start, prev_end, accessible_store_ids)
    prev_result = await db.execute(prev_query)
    prev_map: dict[int, dict[str, float]] = {}
    for row in prev_result.all():
        sid = row[0]
        rev = _to_float(row[1])
        profit = _to_float(row[2])
        oc = _to_float(row[3])
        nr = _to_float(row[4])
        prev_map[sid] = {
            "revenue": rev,
            "profit": profit,
            "order_count": oc,
            "avg_order_value": round(nr / oc, 2) if oc > 0 else 0.0,
        }

    # 查询门店名称
    all_store_ids = set(current_map.keys()) | set(prev_map.keys())
    if not all_store_ids:
        return []

    store_query = select(Store.id, Store.name).where(Store.id.in_(list(all_store_ids)))
    store_result = await db.execute(store_query)
    store_names = {row[0]: row[1] for row in store_result.all()}

    # 组装结果
    items: list[StoreComparisonItem] = []
    for sid in sorted(all_store_ids):
        cur = current_map.get(sid, {})
        prev = prev_map.get(sid, {})

        cur_rev = cur.get("revenue", 0.0)
        prev_rev = prev.get("revenue", 0.0)
        cur_profit = cur.get("profit", 0.0)
        prev_profit = prev.get("profit", 0.0)
        cur_oc = int(cur.get("order_count", 0))
        prev_oc = int(prev.get("order_count", 0))
        cur_aov = cur.get("avg_order_value", 0.0)
        prev_aov = prev.get("avg_order_value", 0.0)

        items.append(
            StoreComparisonItem(
                store_id=sid,
                store_name=store_names.get(sid, f"门店{sid}"),
                current_revenue=round(cur_rev, 2),
                previous_revenue=round(prev_rev, 2),
                revenue_growth_rate=_calc_growth_rate(cur_rev, prev_rev),
                current_profit=round(cur_profit, 2),
                previous_profit=round(prev_profit, 2),
                profit_growth_rate=_calc_growth_rate(cur_profit, prev_profit),
                current_order_count=cur_oc,
                previous_order_count=prev_oc,
                order_growth_rate=_calc_growth_rate(float(cur_oc), float(prev_oc)),
                current_avg_order_value=round(cur_aov, 2),
                previous_avg_order_value=round(prev_aov, 2),
                avg_order_value_growth_rate=_calc_growth_rate(cur_aov, prev_aov),
            )
        )

    return items
