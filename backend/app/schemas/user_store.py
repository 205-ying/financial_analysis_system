"""
用户门店权限相关 Schema 定义
"""

from typing import List

from pydantic import BaseModel, Field


class UserStoreAssignRequest(BaseModel):
    """分配门店权限请求"""

    user_id: int = Field(..., description="用户ID")
    store_ids: List[int] = Field(..., description="门店ID列表")
