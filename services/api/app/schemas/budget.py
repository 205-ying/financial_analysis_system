from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BudgetBase(BaseModel):
    amount: Decimal = Field(..., ge=0, description="预算金额")


class BudgetCreate(BudgetBase):
    store_id: int = Field(..., gt=0, description="门店ID")
    expense_type_id: int = Field(..., gt=0, description="费用科目ID")
    year: int = Field(..., ge=2000, le=2100, description="年份")
    month: int = Field(..., ge=1, le=12, description="月份")


class BudgetItemCreate(BaseModel):
    expense_type_id: int = Field(..., gt=0, description="费用科目ID")
    amount: float = Field(..., ge=0, description="预算金额")


class BudgetBatchCreate(BaseModel):
    store_id: int = Field(..., gt=0, description="门店ID")
    year: int = Field(..., ge=2000, le=2100, description="年份")
    month: int = Field(..., ge=1, le=12, description="月份")
    items: list[BudgetItemCreate] = Field(..., min_length=1, description="预算条目")


class BudgetUpdate(BudgetBase):
    pass


class BudgetSchema(BudgetBase):
    id: int
    store_id: int
    expense_type_id: int
    year: int
    month: int
    created_at: datetime
    updated_at: datetime
    created_by_id: Optional[int]
    updated_by_id: Optional[int]

    class Config:
        from_attributes = True


class BudgetAnalysisItem(BaseModel):
    expense_type_id: int
    expense_type_name: str
    budget_amount: float
    actual_amount: float
    variance: float  # 差异额 = 实际 - 预算
    variance_rate: float  # 差异率 = (实际 - 预算) / 预算 * 100
    is_over_budget: bool  # 是否超支


class BudgetAnalysisResponse(BaseModel):
    total_budget: float
    total_actual: float
    total_variance: float
    items: list[BudgetAnalysisItem]
