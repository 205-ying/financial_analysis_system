"""
KPI 数据 API
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, date

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.kpi import KpiDailyStore
from app.models.store import Store
from app.models.order import OrderHeader
from app.models.expense import ExpenseRecord, ExpenseType
from app.schemas.common import Response, success
from app.schemas.kpi import KpiRebuildRequest
from app.services.kpi_calculator import KpiCalculator
from app.services.audit import create_audit_log
from app.services.data_scope_service import filter_stores_by_access, assert_store_access
from decimal import Decimal

router = APIRouter()


@router.get(
    "/daily",
    response_model=Response[List[Dict[str, Any]]],
    summary="获取日常KPI数据",
    description="获取门店日常KPI数据"
)
async def get_daily_kpi(
    store_id: int = Query(None, description="门店ID"),
    date_from: date = Query(None, description="开始日期"),
    date_to: date = Query(None, description="结束日期"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取日常KPI数据"""
    # 数据权限过滤：获取可访问的门店ID列表
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    
    query = select(KpiDailyStore)
    
    # 应用数据权限过滤
    if accessible_store_ids is not None:
        query = query.where(KpiDailyStore.store_id.in_(accessible_store_ids))
    
    # 应用筛选条件
    if date_from:
        query = query.where(KpiDailyStore.biz_date >= date_from)
    if date_to:
        query = query.where(KpiDailyStore.biz_date <= date_to)
    
    query = query.order_by(KpiDailyStore.biz_date.desc()).limit(100)
    
    result = await db.execute(query)
    kpi_data = result.scalars().all()
    
    return success(
        data=[{
            "id": kpi.id,
            "store_id": kpi.store_id,
            "business_date": kpi.biz_date.isoformat(),
            "sales_amount": float(kpi.revenue),
            "order_count": kpi.order_count,
            "customer_count": kpi.customer_count,
            "avg_order_value": float(kpi.avg_order_value) if kpi.avg_order_value else 0
        } for kpi in kpi_data]
    )


@router.get(
    "/summary",
    response_model=Response[Dict[str, Any]],
    summary="获取KPI汇总数据",
    description="获取KPI汇总统计数据"
)
async def get_kpi_summary(
    start_date: date = Query(None, description="开始日期"),
    end_date: date = Query(None, description="结束日期"),
    store_id: int = Query(None, description="门店ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取KPI汇总数据"""
    from sqlalchemy import and_
    
    # 如果没有指定日期范围，默认使用当月
    if not start_date:
        start_date = date.today().replace(day=1)
    if not end_date:
        end_date = date.today()
    
    # 数据权限过滤：获取可访问的门店ID列表
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    
    # 构建查询条件
    conditions = [
        KpiDailyStore.biz_date >= start_date,
        KpiDailyStore.biz_date <= end_date
    ]
    if accessible_store_ids is not None:
        conditions.append(KpiDailyStore.store_id.in_(accessible_store_ids))
    
    # 获取总营收
    revenue_result = await db.execute(
        select(func.sum(KpiDailyStore.revenue)).where(and_(*conditions))
    )
    total_revenue = float(revenue_result.scalar() or 0)
    
    # 获取总订单数
    orders_result = await db.execute(
        select(func.sum(KpiDailyStore.order_count)).where(and_(*conditions))
    )
    order_count = int(orders_result.scalar() or 0)
    
    # 获取总成本（从费用记录）
    expense_conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date
    ]
    if accessible_store_ids is not None:
        expense_conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))
    
    cost_result = await db.execute(
        select(func.sum(ExpenseRecord.amount)).where(and_(*expense_conditions))
    )
    total_cost = float(cost_result.scalar() or 0)
    
    # 获取费用记录数
    expense_count_result = await db.execute(
        select(func.count(ExpenseRecord.id)).where(and_(*expense_conditions))
    )
    expense_count = int(expense_count_result.scalar() or 0)
    
    # 获取门店数量
    store_count_result = await db.execute(
        select(func.count(func.distinct(KpiDailyStore.store_id))).where(and_(*conditions))
    )
    store_count = int(store_count_result.scalar() or 0)
    
    # 计算利润和利润率
    total_profit = total_revenue - total_cost
    profit_rate = (total_profit / total_revenue) if total_revenue > 0 else 0
    
    return success(
        data={
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "total_profit": total_profit,
            "profit_rate": profit_rate,
            "order_count": order_count,
            "expense_count": expense_count,
            "store_count": store_count,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    )


@router.get(
    "/trend",
    response_model=Response[Dict[str, Any]],
    summary="获取KPI趋势数据",
    description="获取KPI趋势数据，支持按日、周、月聚合"
)
async def get_kpi_trend(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    store_id: int = Query(None, description="门店ID"),
    granularity: str = Query("day", description="粒度：day/week/month"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取KPI趋势数据"""
    from sqlalchemy import and_, cast
    
    # 数据权限过滤：获取可访问的门店ID列表
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    
    # 查询订单数据，将order_time转换为日期
    order_date_expr = func.date(OrderHeader.order_time)
    query = select(
        order_date_expr.label('order_date'),
        func.sum(OrderHeader.net_amount).label('revenue'),
        func.count(OrderHeader.id).label('order_count')
    )
    
    conditions = [
        func.date(OrderHeader.order_time) >= start_date,
        func.date(OrderHeader.order_time) <= end_date
    ]
    
    if accessible_store_ids is not None:
        conditions.append(OrderHeader.store_id.in_(accessible_store_ids))
    
    query = query.where(and_(*conditions))
    query = query.group_by(order_date_expr)
    query = query.order_by(order_date_expr)
    
    result = await db.execute(query)
    order_data = result.all()
    
    # 查询费用数据
    expense_query = select(
        ExpenseRecord.biz_date,
        func.sum(ExpenseRecord.amount).label('cost')
    )
    
    expense_conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date
    ]
    
    if accessible_store_ids is not None:
        expense_conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))
    
    expense_query = expense_query.where(and_(*expense_conditions))
    expense_query = expense_query.group_by(ExpenseRecord.biz_date)
    
    expense_result = await db.execute(expense_query)
    expense_data = {row.biz_date: row.cost for row in expense_result.all()}
    
    # 合并数据
    trend_items = []
    for row in order_data:
        order_date = row.order_date
        revenue = float(row.revenue or 0)
        cost = float(expense_data.get(order_date, 0))
        profit = revenue - cost
        
        trend_items.append({
            "date": order_date.isoformat(),
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "order_count": row.order_count
        })
    
    # 按粒度聚合（简化版，实际应该更复杂）
    if granularity in ["week", "month"]:
        # 这里简化处理，实际应该按周或月聚合
        pass
    
    # 计算汇总
    summary = {
        "total_revenue": sum(item["revenue"] for item in trend_items),
        "total_cost": sum(item["cost"] for item in trend_items),
        "total_profit": sum(item["profit"] for item in trend_items),
        "total_orders": sum(item["order_count"] for item in trend_items),
        "data_points": len(trend_items)
    }
    
    return success(
        data={
            "items": trend_items,
            "summary": summary,
            "granularity": granularity,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    )


@router.get(
    "/expense-category",
    response_model=Response[Dict[str, Any]],
    summary="获取费用分类统计",
    description="按费用类型统计费用金额和占比"
)
async def get_expense_category(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    store_id: int = Query(None, description="门店ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取费用分类统计"""
    from sqlalchemy import and_
    from sqlalchemy.orm import selectinload
    
    # 数据权限过滤：获取可访问的门店ID列表
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    
    # 查询费用记录
    query = select(
        ExpenseType.name.label('category_name'),
        func.sum(ExpenseRecord.amount).label('total_amount'),
        func.count(ExpenseRecord.id).label('record_count')
    ).join(ExpenseType, ExpenseRecord.expense_type_id == ExpenseType.id)
    
    conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date
    ]
    
    if accessible_store_ids is not None:
        conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))
    
    query = query.where(and_(*conditions))
    query = query.group_by(ExpenseType.name)
    query = query.order_by(func.sum(ExpenseRecord.amount).desc())
    
    result = await db.execute(query)
    categories_data = result.all()
    
    # 计算总额和占比
    total_amount = sum(float(row.total_amount or 0) for row in categories_data)
    
    categories = []
    for row in categories_data:
        amount = float(row.total_amount or 0)
        percentage = (amount / total_amount * 100) if total_amount > 0 else 0
        
        categories.append({
            "category_name": row.category_name,
            "amount": amount,
            "record_count": row.record_count,
            "percentage": round(percentage, 2)
        })
    
    return success(
        data={
            "categories": categories,
            "total_amount": total_amount,
            "total_categories": len(categories),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    )


@router.get(
    "/store-ranking",
    response_model=Response[Dict[str, Any]],
    summary="获取门店排名",
    description="按营收、利润或利润率对门店进行排名"
)
async def get_store_ranking(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    top_n: int = Query(999, description="Top N，999表示全部"),
    sort_by: str = Query("profit", description="排序字段：revenue/profit/profit_margin"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取门店排名"""
    from sqlalchemy import and_
    
    # 数据权限过滤：获取可访问的门店ID列表
    accessible_store_ids = await filter_stores_by_access(db, current_user, None)
    
    # 查询订单数据（按门店）
    order_query = select(
        Store.id.label('store_id'),
        Store.name.label('store_name'),
        func.sum(OrderHeader.net_amount).label('revenue'),
        func.count(OrderHeader.id).label('order_count')
    ).join(Store, OrderHeader.store_id == Store.id)
    
    order_conditions = [
        func.date(OrderHeader.order_time) >= start_date,
        func.date(OrderHeader.order_time) <= end_date
    ]
    if accessible_store_ids is not None:
        order_conditions.append(OrderHeader.store_id.in_(accessible_store_ids))
    
    order_query = order_query.where(and_(*order_conditions))
    order_query = order_query.group_by(Store.id, Store.name)
    
    order_result = await db.execute(order_query)
    order_data = {row.store_id: row for row in order_result.all()}
    
    # 查询费用数据（按门店）
    expense_query = select(
        ExpenseRecord.store_id,
        func.sum(ExpenseRecord.amount).label('cost')
    )
    
    expense_conditions = [
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date
    ]
    if accessible_store_ids is not None:
        expense_conditions.append(ExpenseRecord.store_id.in_(accessible_store_ids))
    
    expense_query = expense_query.where(and_(*expense_conditions))
    expense_query = expense_query.group_by(ExpenseRecord.store_id)
    
    expense_result = await db.execute(expense_query)
    expense_data = {row.store_id: float(row.cost or 0) for row in expense_result.all()}
    
    # 合并数据并计算利润
    stores = []
    for store_id, order_row in order_data.items():
        revenue = float(order_row.revenue or 0)
        cost = expense_data.get(store_id, 0)
        profit = revenue - cost
        profit_margin = (profit / revenue * 100) if revenue > 0 else 0
        
        stores.append({
            "store_id": store_id,
            "store_name": order_row.store_name,
            "revenue": revenue,
            "cost": cost,
            "profit": profit,
            "profit_margin": round(profit_margin, 2),
            "order_count": order_row.order_count
        })
    
    # 排序
    sort_key_map = {
        "revenue": lambda x: x["revenue"],
        "profit": lambda x: x["profit"],
        "profit_margin": lambda x: x["profit_margin"]
    }
    
    sort_key = sort_key_map.get(sort_by, sort_key_map["profit"])
    stores.sort(key=sort_key, reverse=True)
    
    # 添加排名
    for rank, store in enumerate(stores, 1):
        store["rank"] = rank
    
    # 限制Top N
    if top_n < 999:
        stores = stores[:top_n]
    
    return success(
        data={
            "stores": stores,
            "total_stores": len(stores),
            "sort_by": sort_by,
            "top_n": top_n if top_n < 999 else "all",
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
    )


@router.post(
    "/rebuild",
    response_model=Response[dict],
    summary="重建KPI数据",
    description="重建指定日期范围的KPI数据（可选指定门店）"
)
async def rebuild_kpi(
    data: KpiRebuildRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    重建KPI数据
    
    重新计算指定日期范围的KPI数据，并更新到数据库中。
    """
    # 验证日期范围
    if data.start_date > data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="开始日期不能大于结束日期"
        )
    
    # 如果指定了门店，验证门店存在并校验数据权限
    if data.store_id:
        await assert_store_access(db, current_user, data.store_id)
        store_result = await db.execute(select(Store).where(Store.id == data.store_id))
        if not store_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="门店不存在"
            )
    
    # 执行重建
    calculator = KpiCalculator(db)
    affected_dates, affected_stores, total_records = await calculator.rebuild_daily_kpi(
        start_date=data.start_date,
        end_date=data.end_date,
        store_id=data.store_id
    )
    
    # 记录审计日志
    await create_audit_log(
        db=db,
        user=current_user,
        action="REBUILD_KPI",
        resource="kpi",
        detail={
            "start_date": data.start_date.isoformat(),
            "end_date": data.end_date.isoformat(),
            "store_id": data.store_id,
            "affected_dates": affected_dates,
            "affected_stores": affected_stores,
            "total_records": total_records
        },
        request=request,
        status_code=200
    )
    await db.commit()
    
    return success(
        data={
            "message": "KPI数据重建完成",
            "affected_dates": affected_dates,
            "affected_stores": affected_stores,
            "total_records": total_records
        }
    )