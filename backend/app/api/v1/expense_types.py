"""
费用科目管理 API
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.expense import ExpenseType
from app.schemas.common import Response, success

router = APIRouter()


@router.get(
    "/all",
    response_model=Response[List[dict]],
    summary="获取所有费用科目",
    description="获取所有激活的费用科目（不分页）"
)
async def get_all_expense_types(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取所有激活的费用科目"""
    result = await db.execute(
        select(ExpenseType).where(ExpenseType.is_active == True).order_by(ExpenseType.category, ExpenseType.name)
    )
    expense_types = result.scalars().all()
    
    return success(
        data=[{
            "id": expense_type.id,
            "name": expense_type.name,
            "category": expense_type.category,
            "description": expense_type.description,
            "is_active": expense_type.is_active
        } for expense_type in expense_types]
    )


@router.get(
    "",
    response_model=Response[List[dict]],
    summary="获取费用科目列表",
    description="获取费用科目列表（支持分页）"
)
async def list_expense_types(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取费用科目列表"""
    result = await db.execute(
        select(ExpenseType).where(ExpenseType.is_active == True).order_by(ExpenseType.category, ExpenseType.name)
    )
    expense_types = result.scalars().all()
    
    return success(
        data=[{
            "id": expense_type.id,
            "name": expense_type.name,
            "category": expense_type.category,
            "description": expense_type.description,
            "is_active": expense_type.is_active
        } for expense_type in expense_types]
    )


@router.get(
    "/{expense_type_id}",
    response_model=Response[dict],
    summary="获取费用科目详情",
    description="获取费用科目详情"
)
async def get_expense_type(
    expense_type_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取费用科目详情"""
    result = await db.execute(select(ExpenseType).where(ExpenseType.id == expense_type_id))
    expense_type = result.scalar_one_or_none()
    
    if not expense_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="费用科目不存在"
        )
    
    return success(
        data={
            "id": expense_type.id,
            "name": expense_type.name,
            "category": expense_type.category,
            "description": expense_type.description,
            "is_active": expense_type.is_active
        }
    )