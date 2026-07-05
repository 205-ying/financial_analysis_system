"""
Finance operations center API.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import check_permission, get_current_user, get_db
from app.models.user import User
from app.schemas.common import Response
from app.schemas.finance import (
    FinanceCloseReadinessOverview,
    FinanceOperationsOverview,
    FinanceSuiteOverview,
)
from app.services import finance_service
from app.services.audit_log_service import log_audit
from app.services.data_scope_service import filter_stores_by_access

router = APIRouter()


@router.get("/operations-overview", response_model=Response[FinanceOperationsOverview])
async def get_operations_overview(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取财务运营中心数据。

    权限: dashboard:view
    """
    await check_permission(current_user, "dashboard:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    data = await finance_service.get_finance_operations_overview(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        accessible_store_ids=accessible_store_ids,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="VIEW",
        request=request,
        resource_type="finance",
        detail={
            "type": "operations_overview",
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    return Response(code=0, message="查询成功", data=data)


@router.get("/suite-overview", response_model=Response[FinanceSuiteOverview])
async def get_suite_overview(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取剩余财务功能全量工作台。

    覆盖总账、银行对账、应收应付、预算审批、固定资产、税务发票、
    关账合并等剩余能力的一期可运行视图。

    权限: dashboard:view
    """
    await check_permission(current_user, "dashboard:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    data = await finance_service.get_finance_suite_overview(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        accessible_store_ids=accessible_store_ids,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="VIEW",
        request=request,
        resource_type="finance",
        detail={
            "type": "suite_overview",
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    return Response(code=0, message="查询成功", data=data)


@router.get("/close-readiness", response_model=Response[FinanceCloseReadinessOverview])
async def get_close_readiness(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取关账准备与银行对账预检查数据。

    权限: dashboard:view
    """
    await check_permission(current_user, "dashboard:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    data = await finance_service.get_finance_close_readiness(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        accessible_store_ids=accessible_store_ids,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="VIEW",
        request=request,
        resource_type="finance",
        detail={
            "type": "close_readiness",
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    return Response(code=0, message="查询成功", data=data)
