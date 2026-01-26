"""
报表中心 API

提供日汇总、月汇总、门店绩效、费用明细等报表查询和导出功能
"""
from datetime import datetime
from urllib.parse import quote
from typing import List

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.models.user import User
from app.schemas.common import Response
from app.schemas.report import (
    DailySummaryRow,
    MonthlySummaryRow,
    StorePerformanceRow,
    ExpenseBreakdownRow,
    ReportQuery
)
from app.services import report_service
from app.services.audit_log_service import log_audit

router = APIRouter()


@router.get("/daily-summary", response_model=Response[List[DailySummaryRow]])
async def get_daily_summary_report(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取日汇总报表
    
    权限: report:view
    """
    # 权限检查
    await check_permission(current_user, "report:view", db)
    
    # 构建查询参数
    from datetime import date
    filters = ReportQuery(
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        store_id=store_id
    )
    
    # 查询数据（传入current_user进行数据权限过滤）
    data = await report_service.get_daily_summary(db, filters, current_user)
    
    return Response(
        code=200,
        message="查询成功",
        data=data
    )


@router.get("/monthly-summary", response_model=Response[List[MonthlySummaryRow]])
async def get_monthly_summary_report(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取月汇总报表
    
    权限: report:view
    """
    # 权限检查
    await check_permission(current_user, "report:view", db)
    
    # 构建查询参数
    from datetime import date
    filters = ReportQuery(
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        store_id=store_id
    )
    
    # 查询数据（传入current_user进行数据权限过滤）
    data = await report_service.get_monthly_summary(db, filters, current_user)
    
    return Response(
        code=200,
        message="查询成功",
        data=data
    )


@router.get("/store-performance", response_model=Response[List[StorePerformanceRow]])
async def get_store_performance_report(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    top_n: int | None = Query(None, ge=1, le=100, description="TOP N排名（1-100）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取门店绩效报表
    
    权限: report:view
    """
    # 权限检查
    await check_permission(current_user, "report:view", db)
    
    # 构建查询参数
    from datetime import date
    filters = ReportQuery(
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        store_id=store_id,
        top_n=top_n
    )
    
    # 查询数据（传入current_user进行数据权限过滤）
    data = await report_service.get_store_performance(db, filters, current_user)
    
    return Response(
        code=200,
        message="查询成功",
        data=data
    )


@router.get("/expense-breakdown", response_model=Response[List[ExpenseBreakdownRow]])
async def get_expense_breakdown_report(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    top_n: int | None = Query(None, ge=1, le=100, description="TOP N排名（1-100）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取费用明细报表
    
    权限: report:view
    """
    # 权限检查
    await check_permission(current_user, "report:view", db)
    
    # 构建查询参数
    from datetime import date
    filters = ReportQuery(
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        store_id=store_id,
        top_n=top_n
    )
    
    # 查询数据（传入current_user进行数据权限过滤）
    data = await report_service.get_expense_breakdown(db, filters, current_user)
    
    return Response(
        code=200,
        message="查询成功",
        data=data
    )


@router.get("/export")
async def export_report(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    导出报表为 Excel 文件
    
    权限: report:export
    """
    # 权限检查
    await check_permission(current_user, "report:export", db)
    
    # 构建查询参数
    from datetime import date
    filters = ReportQuery(
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        store_id=store_id
    )
    
    # 生成Excel（传入current_user进行数据权限过滤）
    excel_bytes = await report_service.export_report_excel(db, filters, current_user)
    
    # 记录审计日志
    await log_audit(
        db=db,
        user_id=current_user.id,
        action="export_report",
        resource_type="report",
        detail={
            "start_date": start_date,
            "end_date": end_date,
            "store_id": store_id,
            "export_time": datetime.now().isoformat()
        }
    )
    
    # 生成文件名
    filename = f"report_{start_date}_{end_date}"
    if store_id:
        filename += f"_store{store_id}"
    filename += ".xlsx"
    encoded_filename = quote(filename)
    
    # 返回文件流
    return StreamingResponse(
        iter([excel_data]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=report.xlsx; filename*=UTF-8''{encoded_filename}"
        }
    )
