"""
菜品销售分析服务

提供菜品销量排行、品类分布、毛利贡献、ABC分类、门店交叉分析等功能。
所有聚合计算在数据库端完成，避免在 Python 中循环处理大量数据。
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OrderHeader, OrderItem
from app.models.store import Store, Product
from app.schemas.product_analysis import (
    ProductSalesRankingItem,
    CategorySalesItem,
    ProductProfitItem,
    ProductABCItem,
    ProductStoreCrossItem,
)


def _to_float(val: Any) -> float:
    """安全地将 Decimal/None 转为 float"""
    if val is None:
        return 0.0
    if isinstance(val, Decimal):
        return float(val)
    return float(val)


def _base_query_filter(
    query: Any,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
) -> Any:
    """为查询添加日期范围和门店权限过滤"""
    query = query.where(OrderHeader.biz_date >= start_date)
    query = query.where(OrderHeader.biz_date <= end_date)
    query = query.where(OrderHeader.status != "cancelled")
    if accessible_store_ids is not None:
        query = query.where(OrderHeader.store_id.in_(accessible_store_ids))
    return query


async def get_product_sales_ranking(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
    top_n: int = 20,
    sort_by: str = "quantity",
) -> list[ProductSalesRankingItem]:
    """
    菜品销量排行榜

    从 order_item JOIN order_header 聚合统计每个菜品的销量、销售额、订单数。
    可选择按销量或销售额排序。
    """
    query = (
        select(
            OrderItem.product_name,
            OrderItem.product_category,
            func.sum(OrderItem.quantity).label("total_quantity"),
            func.sum(OrderItem.line_amount).label("total_revenue"),
            func.sum(
                OrderItem.line_amount - func.coalesce(OrderItem.discount_amount, 0)
            ).label("net_revenue"),
            func.count(func.distinct(OrderHeader.id)).label("order_count"),
        )
        .join(OrderHeader, OrderItem.order_id == OrderHeader.id)
    )

    query = _base_query_filter(query, start_date, end_date, accessible_store_ids)
    query = query.group_by(OrderItem.product_name, OrderItem.product_category)

    if sort_by == "revenue":
        query = query.order_by(desc("total_revenue"))
    else:
        query = query.order_by(desc("total_quantity"))

    query = query.limit(top_n)

    result = await db.execute(query)
    rows = result.all()

    # 尝试获取成本价用于毛利计算
    product_costs: dict[str, float] = {}
    if rows:
        product_names = [r.product_name for r in rows]
        cost_result = await db.execute(
            select(Product.name, Product.cost_price)
            .where(Product.name.in_(product_names))
            .where(Product.cost_price.isnot(None))
        )
        for cr in cost_result.all():
            product_costs[cr.name] = _to_float(cr.cost_price)

    items = []
    for rank, row in enumerate(rows, 1):
        net_rev = _to_float(row.net_revenue)
        qty = _to_float(row.total_quantity)
        cost_price = product_costs.get(row.product_name)
        gross_profit = None
        if cost_price is not None:
            gross_profit = round(net_rev - qty * cost_price, 2)

        items.append(
            ProductSalesRankingItem(
                rank=rank,
                product_name=row.product_name,
                product_category=row.product_category,
                total_quantity=round(qty, 3),
                total_revenue=round(_to_float(row.total_revenue), 2),
                net_revenue=round(net_rev, 2),
                order_count=int(row.order_count),
                gross_profit=gross_profit,
            )
        )

    return items


async def get_category_sales_distribution(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
) -> list[CategorySalesItem]:
    """
    品类销售占比

    按 product_category 快照字段聚合销售额和销量，
    计算各品类的营收占比百分比。
    """
    query = (
        select(
            func.coalesce(OrderItem.product_category, "未分类").label("category_name"),
            func.sum(OrderItem.line_amount).label("revenue"),
            func.sum(OrderItem.quantity).label("quantity"),
        )
        .join(OrderHeader, OrderItem.order_id == OrderHeader.id)
    )

    query = _base_query_filter(query, start_date, end_date, accessible_store_ids)
    query = query.group_by(OrderItem.product_category)
    query = query.order_by(desc("revenue"))

    result = await db.execute(query)
    rows = result.all()

    total_revenue = sum(_to_float(r.revenue) for r in rows)

    items = []
    for row in rows:
        rev = _to_float(row.revenue)
        pct = round(rev / total_revenue * 100, 2) if total_revenue > 0 else 0.0
        items.append(
            CategorySalesItem(
                category_name=row.category_name,
                revenue=round(rev, 2),
                quantity=round(_to_float(row.quantity), 3),
                percentage=pct,
            )
        )

    return items


async def get_product_profit_contribution(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
    top_n: int = 20,
) -> list[ProductProfitItem]:
    """
    菜品毛利贡献排行

    通过 order_item LEFT JOIN product 获取成本价，
    计算每个菜品的毛利贡献 = 净销售额 - 数量 × 成本价。
    """
    query = (
        select(
            OrderItem.product_name,
            OrderItem.product_category,
            func.sum(
                OrderItem.line_amount - func.coalesce(OrderItem.discount_amount, 0)
            ).label("total_revenue"),
            func.sum(
                OrderItem.quantity * func.coalesce(Product.cost_price, 0)
            ).label("total_cost"),
        )
        .join(OrderHeader, OrderItem.order_id == OrderHeader.id)
        .outerjoin(Product, OrderItem.product_id == Product.id)
    )

    query = _base_query_filter(query, start_date, end_date, accessible_store_ids)
    query = query.group_by(OrderItem.product_name, OrderItem.product_category)
    query = query.order_by(desc(
        func.sum(OrderItem.line_amount - func.coalesce(OrderItem.discount_amount, 0))
        - func.sum(OrderItem.quantity * func.coalesce(Product.cost_price, 0))
    ))
    query = query.limit(top_n)

    result = await db.execute(query)
    rows = result.all()

    items = []
    for rank, row in enumerate(rows, 1):
        revenue = _to_float(row.total_revenue)
        cost = _to_float(row.total_cost)
        profit = round(revenue - cost, 2)
        margin = round(profit / revenue * 100, 2) if revenue > 0 else 0.0

        items.append(
            ProductProfitItem(
                rank=rank,
                product_name=row.product_name,
                product_category=row.product_category,
                total_revenue=round(revenue, 2),
                total_cost=round(cost, 2),
                gross_profit=profit,
                profit_margin=margin,
            )
        )

    return items


async def get_product_abc_classification(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
) -> list[ProductABCItem]:
    """
    菜品ABC分类

    按销售额降序排列所有菜品，计算累计占比：
    - A类: 累计占比 ≤ 70%（核心菜品）
    - B类: 累计占比 ≤ 90%（重要菜品）
    - C类: 累计占比 > 90%（长尾菜品）
    """
    query = (
        select(
            OrderItem.product_name,
            func.sum(OrderItem.line_amount).label("total_revenue"),
        )
        .join(OrderHeader, OrderItem.order_id == OrderHeader.id)
    )

    query = _base_query_filter(query, start_date, end_date, accessible_store_ids)
    query = query.group_by(OrderItem.product_name)
    query = query.order_by(desc("total_revenue"))

    result = await db.execute(query)
    rows = result.all()

    total_revenue = sum(_to_float(r.total_revenue) for r in rows)

    items = []
    cumulative = 0.0
    for row in rows:
        rev = _to_float(row.total_revenue)
        pct = round(rev / total_revenue * 100, 2) if total_revenue > 0 else 0.0
        cumulative += pct

        if cumulative <= 70:
            abc_class = "A"
        elif cumulative <= 90:
            abc_class = "B"
        else:
            abc_class = "C"

        items.append(
            ProductABCItem(
                product_name=row.product_name,
                total_revenue=round(rev, 2),
                percentage=pct,
                cumulative_percentage=round(cumulative, 2),
                abc_class=abc_class,
            )
        )

    return items


async def get_product_store_cross_analysis(
    db: AsyncSession,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None,
    top_n: int = 10,
) -> list[ProductStoreCrossItem]:
    """
    菜品-门店交叉分析

    按门店和菜品维度聚合销量和销售额，
    展示每个门店中各菜品的销售表现。
    """
    # 先找出 Top N 菜品（按总销售额）
    top_products_query = (
        select(OrderItem.product_name)
        .join(OrderHeader, OrderItem.order_id == OrderHeader.id)
    )
    top_products_query = _base_query_filter(
        top_products_query, start_date, end_date, accessible_store_ids
    )
    top_products_query = (
        top_products_query
        .group_by(OrderItem.product_name)
        .order_by(desc(func.sum(OrderItem.line_amount)))
        .limit(top_n)
    )

    top_result = await db.execute(top_products_query)
    top_product_names = [r.product_name for r in top_result.all()]

    if not top_product_names:
        return []

    # 按门店×菜品聚合
    query = (
        select(
            Store.name.label("store_name"),
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label("quantity"),
            func.sum(OrderItem.line_amount).label("revenue"),
        )
        .join(OrderHeader, OrderItem.order_id == OrderHeader.id)
        .join(Store, OrderHeader.store_id == Store.id)
        .where(OrderItem.product_name.in_(top_product_names))
    )

    query = _base_query_filter(query, start_date, end_date, accessible_store_ids)
    query = query.group_by(Store.name, OrderItem.product_name)
    query = query.order_by(Store.name, desc("revenue"))

    result = await db.execute(query)
    rows = result.all()

    items = []
    for row in rows:
        items.append(
            ProductStoreCrossItem(
                store_name=row.store_name,
                product_name=row.product_name,
                quantity=round(_to_float(row.quantity), 3),
                revenue=round(_to_float(row.revenue), 2),
            )
        )

    return items
