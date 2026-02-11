from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class BudgetBase(BaseModel):
    amount: Decimal = Field(..., description="预算金额")

class BudgetCreate(BudgetBase):
    store_id: int = Field(..., description="门店ID")
    expense_type_id: int = Field(..., description="费用科目ID")
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")

class BudgetItemCreate(BaseModel):
    expense_type_id: int
    amount: float

class BudgetBatchCreate(BaseModel):
    store_id: int
    year: int
    month: int
    items: List[BudgetItemCreate]


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
    variance: float        # 差异额 = 实际 - 预算
    variance_rate: float   # 差异率 = (实际 - 预算) / 预算 * 100
    is_over_budget: bool   # 是否超支

class BudgetAnalysisResponse(BaseModel):
    total_budget: float
    total_actual: float
    total_variance: float
    items: List[BudgetAnalysisItem]
