"""
费用记录相关 Schema 定义
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class ExpenseRecordCreate(BaseModel):
    """创建费用记录请求"""

    store_id: int = Field(..., description="门店ID")
    expense_type_id: int = Field(..., description="费用类型ID")
    biz_date: date = Field(..., description="业务日期")
    amount: Decimal = Field(..., description="金额")
    remark: str = Field("", description="备注")


class ExpenseRecordUpdate(BaseModel):
    """更新费用记录请求"""

    store_id: Optional[int] = Field(None, description="门店ID")
    expense_type_id: Optional[int] = Field(None, description="费用类型ID")
    biz_date: Optional[date] = Field(None, description="业务日期")
    amount: Optional[Decimal] = Field(None, description="金额")
    remark: Optional[str] = Field(None, description="备注")
