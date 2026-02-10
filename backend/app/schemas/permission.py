"""
权限管理相关的 Schema 定义
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PermissionBase(BaseModel):
    """权限基础信息"""
    code: str = Field(..., description="权限编码", max_length=100)
    name: str = Field(..., description="权限名称", max_length=100)
    resource: str = Field(..., description="资源标识", max_length=100)
    action: str = Field(..., description="操作类型", max_length=50)
    description: Optional[str] = Field(None, description="权限描述")


class PermissionCreate(PermissionBase):
    """创建权限"""
    pass


class PermissionUpdate(BaseModel):
    """更新权限"""
    name: Optional[str] = Field(None, description="权限名称")
    description: Optional[str] = Field(None, description="权限描述")


class PermissionSchema(PermissionBase):
    """权限详情"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PermissionListItem(BaseModel):
    """权限列表项"""
    id: int
    code: str
    name: str
    resource: str
    action: str
    description: Optional[str]
    role_count: int = Field(0, description="使用该权限的角色数量")
    created_at: datetime

    class Config:
        from_attributes = True
