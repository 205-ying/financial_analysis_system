"""
角色管理相关的 Schema 定义
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class PermissionBase(BaseModel):
    """权限基础信息"""
    code: str = Field(..., description="权限编码")
    name: str = Field(..., description="权限名称")
    resource: str = Field(..., description="资源标识")
    action: str = Field(..., description="操作类型")
    description: Optional[str] = Field(None, description="权限描述")


class PermissionSchema(PermissionBase):
    """权限详情"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """角色基础信息"""
    code: str = Field(..., description="角色编码", max_length=50)
    name: str = Field(..., description="角色名称", max_length=100)
    description: Optional[str] = Field(None, description="角色描述")
    is_active: bool = Field(True, description="是否启用")


class RoleCreate(RoleBase):
    """创建角色"""
    permission_ids: List[int] = Field(default_factory=list, description="权限ID列表")


class RoleUpdate(BaseModel):
    """更新角色"""
    name: Optional[str] = Field(None, description="角色名称")
    description: Optional[str] = Field(None, description="角色描述")
    is_active: Optional[bool] = Field(None, description="是否启用")


class RoleSchema(RoleBase):
    """角色详情"""
    id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionSchema] = Field(default_factory=list, description="权限列表")

    class Config:
        from_attributes = True


class RoleListItem(BaseModel):
    """角色列表项"""
    id: int
    code: str
    name: str
    description: Optional[str]
    is_active: bool
    permission_count: int = Field(0, description="权限数量")
    user_count: int = Field(0, description="用户数量")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignPermissionsRequest(BaseModel):
    """分配权限请求"""
    permission_ids: List[int] = Field(..., description="权限ID列表")
