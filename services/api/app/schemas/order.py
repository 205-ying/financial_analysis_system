"""
订单相关 Schema 定义
"""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    """创建订单请求"""

    store_id: int = Field(..., description="门店ID")
    channel: str = Field(..., description="渠道")
    order_no: str = Field(..., description="订单号")
    net_amount: Decimal = Field(..., description="订单金额")
    order_time: datetime = Field(..., description="订单时间")
    remark: str = Field("", description="备注")
