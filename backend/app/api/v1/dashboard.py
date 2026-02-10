"""
Dashboard 仪表盘 API

提供管理驾驶舱聚合数据接口，一次请求返回全部数据。
"""

from datetime import date

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.models.user import User
from app.schemas.common import Response
from app.schemas.dashboard import DashboardOverview
from app.services import dashboard_service
from app.services.audit_log_service import log_audit
from app.services.data_scope_service import filter_stores_by_access

router = APIRouter()


@router.get("/overview", response_model=Response[DashboardOverview])
async def get_dashboard_overview(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取仪表盘全量数据

    一次请求返回: 核心指标卡片(含同比/环比) + 趋势 + 门店排名 + 费用结构 + 渠道分布 + 利润率

    权限: dashboard:view
    """
    await check_permission(current_user, "dashboard:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await dashboard_service.get_dashboard_overview(
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
        resource_type="dashboard",
        detail={
            "type": "dashboard_overview",
            "start_date": start_date,
            "end_date": end_date,
        },
    )

    return Response(code=0, message="查询成功", data=data)
