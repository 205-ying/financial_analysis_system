from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal

from app.models.expense import ExpenseType, ExpenseRecord
from app.models.kpi import KpiDailyStore
from app.schemas.cvp import CVPAnalysisResult, CVPSimulationResult

async def update_cost_behavior(
    db: AsyncSession,
    expense_type_id: int,
    cost_behavior: str
):
    """
    更新费用类型的成本习性
    """
    stmt = select(ExpenseType).where(ExpenseType.id == expense_type_id)
    result = await db.execute(stmt)
    expense_type = result.scalar_one_or_none()
    
    if not expense_type:
        raise ValueError(f"费用类型 {expense_type_id} 不存在")
    
    if cost_behavior not in ['fixed', 'variable']:
        raise ValueError("cost_behavior 必须是 'fixed' 或 'variable'")
    
    expense_type.cost_behavior = cost_behavior
    await db.commit()

async def calculate_cvp(
    db: AsyncSession,
    store_id: int | None,
    start_date: date,
    end_date: date,
    accessible_store_ids: list[int] | None = None
) -> CVPAnalysisResult:
    """
    计算本量利分析指标
    
    简化逻辑：
    - 总收入来自 KPI 表的 revenue
    - 变动成本 = KPI 表的 cost_material（原材料成本，主要变动成本） + expense_records 中标记为 variable 的费用
    - 固定成本 = expense_records 中标记为 fixed 的费用
    """
    # 1. 获取总收入和原材料成本（从 KPI 表）
    kpi_query = select(
        func.sum(KpiDailyStore.revenue),
        func.sum(KpiDailyStore.cost_material),
        func.sum(KpiDailyStore.operating_profit)
    ).where(
        KpiDailyStore.biz_date >= start_date,
        KpiDailyStore.biz_date <= end_date
    )
    
    if store_id:
        kpi_query = kpi_query.where(KpiDailyStore.store_id == store_id)
    elif accessible_store_ids:
        kpi_query = kpi_query.where(KpiDailyStore.store_id.in_(accessible_store_ids))
    
    result = await db.execute(kpi_query)
    kpi_row = result.one()
    
    total_revenue = float(kpi_row[0] or 0)
    material_cost = float(kpi_row[1] or 0)  # 原材料成本（变动）
    
    # 2. 获取费用记录中的固定成本和变动成本
    # 先获取所有费用类型的成本习性
    stmt = select(ExpenseType.id, ExpenseType.cost_behavior)
    result = await db.execute(stmt)
    cost_behaviors = {row[0]: row[1] for row in result.all()}
    
    # 查询费用记录
    expense_query = select(
        ExpenseRecord.expense_type_id,
        func.sum(ExpenseRecord.amount)
    ).where(
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date,
        ExpenseRecord.status.in_(['approved', 'paid']),
        ExpenseRecord.is_deleted == False
    )
    
    if store_id:
        expense_query = expense_query.where(ExpenseRecord.store_id == store_id)
    elif accessible_store_ids:
        expense_query = expense_query.where(ExpenseRecord.store_id.in_(accessible_store_ids))
    
    expense_query = expense_query.group_by(ExpenseRecord.expense_type_id)
    
    result = await db.execute(expense_query)
    expense_data = result.all()
    
    # 分类汇总
    fixed_cost_from_expense = Decimal('0.00')
    variable_cost_from_expense = Decimal('0.00')
    
    for etype_id, amount in expense_data:
        behavior = cost_behaviors.get(etype_id, 'variable')
        if behavior == 'fixed':
            fixed_cost_from_expense += amount
        else:
            variable_cost_from_expense += amount
    
    # 3. 计算总变动成本和固定成本
    total_variable_cost = material_cost + float(variable_cost_from_expense)
    total_fixed_cost = float(fixed_cost_from_expense)
    
    # 4. 计算 CVP 指标
    # 边际贡献
    contribution_margin = total_revenue - total_variable_cost
    contribution_margin_rate = (contribution_margin / total_revenue * 100) if total_revenue > 0 else 0
    
    # 盈亏平衡点 BEP = 固定成本 / 边际贡献率
    break_even_point = (total_fixed_cost / (contribution_margin_rate / 100)) if contribution_margin_rate > 0 else 0
    break_even_sales_ratio = (break_even_point / total_revenue * 100) if total_revenue > 0 else 0
    
    # 安全边际
    safety_margin = total_revenue - break_even_point
    safety_margin_rate = (safety_margin / total_revenue * 100) if total_revenue > 0 else 0
    
    # 经营利润
    operating_profit = contribution_margin - total_fixed_cost
    
    # 经营杠杆系数
    operating_leverage = (contribution_margin / operating_profit) if operating_profit != 0 else 0
    
    return CVPAnalysisResult(
        total_revenue=total_revenue,
        variable_cost=total_variable_cost,
        fixed_cost=total_fixed_cost,
        contribution_margin=contribution_margin,
        contribution_margin_rate=contribution_margin_rate,
        break_even_point=break_even_point,
        break_even_sales_ratio=break_even_sales_ratio,
        safety_margin=safety_margin,
        safety_margin_rate=safety_margin_rate,
        operating_leverage=operating_leverage,
        operating_profit=operating_profit
    )

async def simulate_cvp(
    db: AsyncSession,
    store_id: int | None,
    start_date: date,
    end_date: date,
    fixed_cost_change_rate: float,
    variable_cost_change_rate: float,
    accessible_store_ids: list[int] | None = None
) -> CVPSimulationResult:
    """
    CVP 敏感性分析模拟
    """
    # 获取原始数据
    original = await calculate_cvp(db, store_id, start_date, end_date, accessible_store_ids)
    
    # 模拟新的成本
    new_fixed_cost = original.fixed_cost * (1 + fixed_cost_change_rate / 100)
    new_variable_cost = original.variable_cost * (1 + variable_cost_change_rate / 100)
    
    # 重新计算边际贡献率
    new_contribution_margin = original.total_revenue - new_variable_cost
    new_contribution_margin_rate = (new_contribution_margin / original.total_revenue * 100) if original.total_revenue > 0 else 0
    
    # 新的盈亏平衡点
    new_bep = (new_fixed_cost / (new_contribution_margin_rate / 100)) if new_contribution_margin_rate > 0 else 0
    
    bep_change = new_bep - original.break_even_point
    bep_change_rate = (bep_change / original.break_even_point * 100) if original.break_even_point > 0 else 0
    
    return CVPSimulationResult(
        original_bep=original.break_even_point,
        simulated_bep=new_bep,
        bep_change=bep_change,
        bep_change_rate=bep_change_rate
    )
