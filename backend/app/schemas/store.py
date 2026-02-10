"""
门店相关数据模型
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class StoreBase(BaseModel):
    """门店基础模型"""
    name: str = Field(..., description="门店名称")
    code: Optional[str] = Field(None, description="门店代码")
    address: Optional[str] = Field(None, description="门店地址")
    city: Optional[str] = Field(None, description="城市")
    phone: Optional[str] = Field(None, description="联系电话")
    manager: Optional[str] = Field(None, description="店长姓名")
    status: Optional[str] = Field("active", description="门店状态")
    is_active: bool = Field(True, description="是否激活")


class StoreCreate(StoreBase):
    """创建门店请求模型"""
    pass


class StoreUpdate(BaseModel):
    """更新门店请求模型"""
    name: Optional[str] = Field(None, description="门店名称")
    code: Optional[str] = Field(None, description="门店代码")
    address: Optional[str] = Field(None, description="门店地址")
    city: Optional[str] = Field(None, description="城市")
    phone: Optional[str] = Field(None, description="联系电话")
    manager: Optional[str] = Field(None, description="店长姓名")
    status: Optional[str] = Field(None, description="门店状态")
    is_active: Optional[bool] = Field(None, description="是否激活")


class StoreInDB(StoreBase):
    """门店数据库模型"""
    id: int = Field(..., description="门店ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    class Config:
        from_attributes = True


class StoreListQuery(BaseModel):
    """门店列表查询参数"""
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=500, description="每页大小，最大500条")
    name: Optional[str] = Field(None, description="门店名称（模糊匹配）")
    city: Optional[str] = Field(None, description="城市")
    is_active: Optional[bool] = Field(None, description="是否激活")
    order_by: Optional[str] = Field("created_at", description="排序字段")
    desc: bool = Field(True, description="是否降序")