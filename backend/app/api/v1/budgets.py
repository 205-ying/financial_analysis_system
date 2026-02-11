from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.schemas.common import Response, success
from app.schemas.budget import BudgetBatchCreate, BudgetAnalysisResponse
from app.models.user import User
from app.services import budget_service

router = APIRouter()

@router.post("/batch", summary="批量保存预算")
async def batch_save_budgets(
    data: BudgetBatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    批量保存某门店某月的预算设置
    """
    await check_permission(current_user, "budget:manage", db)
    await budget_service.batch_save_budgets(
        db, 
        data.store_id, 
        data.year, 
        data.month, 
        data.items, 
        current_user
    )
    return success(message="预算保存成功")

@router.get("/analysis", response_model=Response[BudgetAnalysisResponse], summary="获取预算分析报表")
async def get_budget_analysis(
    store_id: int = Query(..., description="门店ID"),
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取预算执行差异分析
    """
    await check_permission(current_user, "budget:view", db)
    data = await budget_service.get_budget_analysis(db, store_id, year, month)
    return success(data=data)
