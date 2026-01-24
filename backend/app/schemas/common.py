"""
通用响应格式和基础 Schema
"""

from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field


DataT = TypeVar("DataT")


class Response(BaseModel, Generic[DataT]):
    """
    统一响应格式
    
    Examples:
        成功响应:
        ```json
        {
            "code": 0,
            "message": "ok",
            "data": {...}
        }
        ```
        
        错误响应:
        ```json
        {
            "code": 40001,
            "message": "用户名或密码错误",
            "data": null
        }
        ```
    """
    code: int = Field(default=0, description="状态码，0 表示成功")
    message: str = Field(default="ok", description="响应消息")
    data: Optional[DataT] = Field(default=None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 0,
                "message": "ok",
                "data": None
            }
        }


def success(data: Any = None, message: str = "ok") -> dict:
    """
    成功响应工厂函数
    
    Args:
        data: 响应数据
        message: 响应消息
        
    Returns:
        dict: 统一格式的成功响应
    """
    return {
        "code": 0,
        "message": message,
        "data": data
    }


def error(code: int, message: str, data: Any = None) -> dict:
    """
    错误响应工厂函数
    
    Args:
        code: 错误码
        message: 错误消息
        data: 附加数据
        
    Returns:
        dict: 统一格式的错误响应
    """
    return {
        "code": code,
        "message": message,
        "data": data
    }


class PageParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")


class PageData(BaseModel, Generic[DataT]):
    """分页数据"""
    items: list[DataT] = Field(description="数据列表")
    total: int = Field(description="总数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    pages: int = Field(description="总页数")
