"""
同比环比时间对比分析 API

提供期间对比汇总、趋势对比、门店对比等接口。
复用 kpi:view 权限。
"""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.models.user import User
from app.schemas.common import Response
from app.schemas.comparison import (
    PeriodComparisonResponse,
    TrendComparisonResponse,
    StoreComparisonItem,
)
from app.services import comparison_service
from app.services.audit_log_service import log_audit
from app.services.data_scope_service import filter_stores_by_access

router = APIRouter()


@router.get("/period", response_model=Response[PeriodComparisonResponse])
async def get_period_comparison(
    request: Request,
    start_date: str = Query(..., description="当期开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="当期结束日期 (YYYY-MM-DD)"),
    compare_type: str = Query("yoy", description="对比类型: yoy/mom/custom"),
    compare_start_date: str | None = Query(None, description="自定义对比期开始日期"),
    compare_end_date: str | None = Query(None, description="自定义对比期结束日期"),
    store_id: int | None = Query(None, description="门店ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取期间对比汇总数据

    权限: kpi:view
    """
    await check_permission(current_user, "kpi:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await comparison_service.get_period_comparison(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        compare_type=compare_type,
        compare_start_date=date.fromisoformat(compare_start_date) if compare_start_date else None,
        compare_end_date=date.fromisoformat(compare_end_date) if compare_end_date else None,
        accessible_store_ids=accessible_store_ids,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="VIEW",
        request=request,
        resource_type="comparison",
        detail={
            "type": "period_comparison",
            "start_date": start_date,
            "end_date": end_date,
            "compare_type": compare_type,
        },
    )

    return Response(code=0, message="查询成功", data=data)


@router.get("/trend", response_model=Response[TrendComparisonResponse])
async def get_trend_comparison(
    request: Request,
    start_date: str = Query(..., description="当期开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="当期结束日期 (YYYY-MM-DD)"),
    metric: str = Query("revenue", description="指标: revenue/net_revenue/operating_profit/order_count/avg_order_value"),
    compare_type: str = Query("yoy", description="对比类型: yoy/mom/custom"),
    compare_start_date: str | None = Query(None, description="自定义对比期开始日期"),
    compare_end_date: str | None = Query(None, description="自定义对比期结束日期"),
    store_id: int | None = Query(None, description="门店ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取趋势对比数据

    权限: kpi:view
    """
    await check_permission(current_user, "kpi:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await comparison_service.get_trend_comparison(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        metric=metric,
        compare_type=compare_type,
        compare_start_date=date.fromisoformat(compare_start_date) if compare_start_date else None,
        compare_end_date=date.fromisoformat(compare_end_date) if compare_end_date else None,
        accessible_store_ids=accessible_store_ids,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="VIEW",
        request=request,
        resource_type="comparison",
        detail={
            "type": "trend_comparison",
            "metric": metric,
            "start_date": start_date,
            "end_date": end_date,
            "compare_type": compare_type,
        },
    )

    return Response(code=0, message="查询成功", data=data)


@router.get("/stores", response_model=Response[List[StoreComparisonItem]])
async def get_store_comparison(
    request: Request,
    start_date: str = Query(..., description="当期开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="当期结束日期 (YYYY-MM-DD)"),
    compare_type: str = Query("yoy", description="对比类型: yoy/mom/custom"),
    compare_start_date: str | None = Query(None, description="自定义对比期开始日期"),
    compare_end_date: str | None = Query(None, description="自定义对比期结束日期"),
    store_id: int | None = Query(None, description="门店ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取门店对比分析数据

    权限: kpi:view
    """
    await check_permission(current_user, "kpi:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await comparison_service.get_store_comparison(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        compare_type=compare_type,
        compare_start_date=date.fromisoformat(compare_start_date) if compare_start_date else None,
        compare_end_date=date.fromisoformat(compare_end_date) if compare_end_date else None,
        accessible_store_ids=accessible_store_ids,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="VIEW",
        request=request,
        resource_type="comparison",
        detail={
            "type": "store_comparison",
            "start_date": start_date,
            "end_date": end_date,
            "compare_type": compare_type,
        },
    )

    return Response(code=0, message="查询成功", data=data)
