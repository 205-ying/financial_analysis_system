from datetime import date
import calendar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from decimal import Decimal

from app.models.budget import Budget
from app.models.expense import ExpenseRecord, ExpenseType
from app.models.user import User
from app.schemas.budget import BudgetAnalysisResponse, BudgetAnalysisItem, BudgetItemCreate

async def batch_save_budgets(
    db: AsyncSession, 
    store_id: int, 
    year: int, 
    month: int, 
    items: list[BudgetItemCreate], 
    user: User
):
    """
    批量保存预算
    :param items: list of BudgetItemCreate
    """
    # 1. 查询该门店、该月已有的预算记录
    stmt = select(Budget).where(
        Budget.store_id == store_id,
        Budget.year == year,
        Budget.month == month
    )
    result = await db.execute(stmt)
    existing_budgets = {b.expense_type_id: b for b in result.scalars().all()}
    
    # 2. 遍历输入项，更新或创建
    for item in items:
        etype_id = item.expense_type_id
        amount = Decimal(str(item.amount)) # 转换为 Decimal
        
        if etype_id in existing_budgets:
            # 更新
            budget = existing_budgets[etype_id]
            budget.amount = amount
            budget.updated_by_id = user.id
        else:
            # 创建
            budget = Budget(
                store_id=store_id,
                expense_type_id=etype_id,
                year=year,
                month=month,
                amount=amount,
                created_by_id=user.id,
                updated_by_id=user.id
            )
            db.add(budget)
            
    await db.commit()

async def get_budget_analysis(
    db: AsyncSession, 
    store_id: int, 
    year: int, 
    month: int
) -> BudgetAnalysisResponse:
    """
    获取预算分析报表
    """
    # 1. 获取所有费用科目
    stmt = select(ExpenseType)
    result = await db.execute(stmt)
    expense_types = result.scalars().all()
    
    # 2. 获取预算数据
    stmt = select(Budget).where(
        Budget.store_id == store_id,
        Budget.year == year,
        Budget.month == month
    )
    result = await db.execute(stmt)
    budgets = {b.expense_type_id: b.amount for b in result.scalars().all()}
    
    # 3. 获取实际费用数据 (Approved/Paid)
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    
    stmt = select(
        ExpenseRecord.expense_type_id,
        func.sum(ExpenseRecord.amount)
    ).where(
        ExpenseRecord.store_id == store_id,
        ExpenseRecord.biz_date >= start_date,
        ExpenseRecord.biz_date <= end_date,
        ExpenseRecord.status.in_(['approved', 'paid']), # 仅统计已审批和已支付
        ExpenseRecord.is_deleted == False
    ).group_by(ExpenseRecord.expense_type_id)
    
    result = await db.execute(stmt)
    actuals = {row[0]: row[1] for row in result.all()}
    
    # 4. 组合数据
    items = []
    total_budget = Decimal('0.00')
    total_actual = Decimal('0.00')
    
    for et in expense_types:
        b_amount = budgets.get(et.id, Decimal('0.00'))
        a_amount = actuals.get(et.id, Decimal('0.00'))
        
        # 计算差异
        variance = a_amount - b_amount
        variance_rate = 0.0
        if b_amount > 0:
            variance_rate = float((variance / b_amount) * 100)
            
        is_over = a_amount > b_amount and b_amount > 0 # 超支判断
        
        items.append(BudgetAnalysisItem(
            expense_type_id=et.id,
            expense_type_name=et.name,
            budget_amount=float(b_amount),
            actual_amount=float(a_amount),
            variance=float(variance),
            variance_rate=variance_rate,
            is_over_budget=is_over
        ))
        
        total_budget += b_amount
        total_actual += a_amount
        
    total_variance = total_actual - total_budget
    
    return BudgetAnalysisResponse(
        total_budget=float(total_budget),
        total_actual=float(total_actual),
        total_variance=float(total_variance),
        items=items
    )
