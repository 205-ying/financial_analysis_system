from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.api.deps import get_db, get_current_user, check_permission
from app.schemas.common import Response, success
from app.schemas.cvp import CVPAnalysisResult, CostBehaviorUpdate, CVPSimulation, CVPSimulationResult
from app.models.user import User
from app.services import cvp_service
from app.services.data_scope_service import filter_stores_by_access

router = APIRouter()

@router.put("/config", summary="设置费用类型成本习性")
async def update_cost_behavior(
    data: CostBehaviorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    设置某个费用类型属于固定成本还是变动成本
    """
    await check_permission(current_user, "decision:cvp", db)
    await cvp_service.update_cost_behavior(db, data.expense_type_id, data.cost_behavior)
    return success(message="成本习性设置成功")

@router.get("/analysis", response_model=Response[CVPAnalysisResult], summary="获取本量利分析")
async def get_cvp_analysis(
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    store_id: int | None = Query(None, description="门店ID，不传则全部门店"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取本量利分析（CVP）结果
    包括：盈亏平衡点、安全边际率、经营杠杆系数等
    """
    await check_permission(current_user, "decision:cvp", db)
    
    # 数据权限过滤
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    
    data = await cvp_service.calculate_cvp(db, store_id, start_date, end_date, accessible_store_ids)
    return success(data=data)

@router.post("/simulate", response_model=Response[CVPSimulationResult], summary="CVP 敏感性分析模拟")
async def simulate_cvp(
    simulation: CVPSimulation,
    start_date: date = Query(..., description="开始日期"),
    end_date: date = Query(..., description="结束日期"),
    store_id: int | None = Query(None, description="门店ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    模拟成本变化对盈亏平衡点的影响
    """
    await check_permission(current_user, "decision:cvp", db)
    
    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)
    
    data = await cvp_service.simulate_cvp(
        db, 
        store_id, 
        start_date, 
        end_date,
        simulation.fixed_cost_change_rate,
        simulation.variable_cost_change_rate,
        accessible_store_ids
    )
    return success(data=data)
