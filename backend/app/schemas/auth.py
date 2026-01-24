"""
认证相关的 Schema
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "Admin@123"
            }
        }


class UserInfo(BaseModel):
    """用户信息"""
    model_config = {"from_attributes": True}
    
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    full_name: Optional[str] = Field(None, description="真实姓名")
    is_active: bool = Field(..., description="是否激活")
    is_superuser: bool = Field(..., description="是否超级管理员")
    roles: list[str] = Field(default_factory=list, description="角色列表")
    permissions: list[str] = Field(default_factory=list, description="权限列表")


class TokenResponse(BaseModel):
    """令牌响应"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user_info: UserInfo = Field(..., description="用户信息")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400,
                "user_info": {
                    "id": 1,
                    "username": "admin",
                    "email": "admin@example.com",
                    "full_name": "系统管理员",
                    "is_active": True,
                    "is_superuser": True,
                    "roles": ["admin"],
                    "permissions": ["*:*:*"]
                }
            }
        }
    }


class RegisterRequest(BaseModel):
    """注册请求（暂不实现）"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=128)
    full_name: Optional[str] = Field(None, max_length=100)
