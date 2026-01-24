"""
审计日志 Schema

用于审计日志的 API 请求和响应数据验证
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AuditLogBase(BaseModel):
    """审计日志基础 Schema"""
    
    action: str = Field(..., description="操作类型", max_length=50)
    resource_type: Optional[str] = Field(None, description="资源类型", max_length=50)
    resource_id: Optional[int] = Field(None, description="资源ID")
    detail: Optional[str] = Field(None, description="操作详情（JSON格式）")
    ip_address: Optional[str] = Field(None, description="客户端IP地址", max_length=45)
    user_agent: Optional[str] = Field(None, description="客户端User-Agent", max_length=255)
    status: str = Field("success", description="操作结果：success/failure/error", max_length=20)
    error_message: Optional[str] = Field(None, description="错误信息")


class AuditLogCreate(AuditLogBase):
    """创建审计日志 Schema"""
    
    user_id: Optional[int] = Field(None, description="操作用户ID")
    username: str = Field(..., description="操作用户名", max_length=50)


class AuditLogResponse(AuditLogBase):
    """审计日志响应 Schema"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="日志ID")
    user_id: Optional[int] = Field(None, description="操作用户ID")
    username: Optional[str] = Field(None, description="操作用户名")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class AuditLogListRequest(BaseModel):
    """审计日志列表查询请求 Schema"""
    
    # 分页参数
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    
    # 筛选参数
    user_id: Optional[int] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, description="用户名（模糊查询）")
    action: Optional[str] = Field(None, description="操作类型")
    resource_type: Optional[str] = Field(None, description="资源类型")
    status: Optional[str] = Field(None, description="操作结果")
    
    # 日期范围
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    
    # 排序
    sort_by: str = Field("created_at", description="排序字段")
    sort_order: str = Field("desc", description="排序方式：asc/desc")


class AuditLogListResponse(BaseModel):
    """审计日志列表响应 Schema"""
    
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    items: list[AuditLogResponse] = Field(..., description="日志列表")


# 审计操作类型枚举（用于文档说明）
class AuditAction:
    """审计操作类型常量"""
    
    # 认证相关
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    
    # 费用相关
    CREATE_EXPENSE = "create_expense"
    UPDATE_EXPENSE = "update_expense"
    DELETE_EXPENSE = "delete_expense"
    BATCH_DELETE_EXPENSE = "batch_delete_expense"
    
    # KPI相关
    REBUILD_KPI = "rebuild_kpi"
    VIEW_KPI = "view_kpi"
    
    # 订单相关
    CREATE_ORDER = "create_order"
    UPDATE_ORDER = "update_order"
    DELETE_ORDER = "delete_order"
    
    # 门店相关
    CREATE_STORE = "create_store"
    UPDATE_STORE = "update_store"
    DELETE_STORE = "delete_store"
    
    # 用户管理相关
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    CHANGE_PASSWORD = "change_password"
    ASSIGN_ROLE = "assign_role"


# 资源类型枚举
class ResourceType:
    """资源类型常量"""
    
    USER = "user"
    ROLE = "role"
    PERMISSION = "permission"
    STORE = "store"
    PRODUCT = "product"
    ORDER = "order"
    EXPENSE = "expense"
    EXPENSE_TYPE = "expense_type"
    KPI = "kpi"
