"""
审计日志 API

提供审计日志查询接口
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user, check_permission
from app.models.user import User
from app.schemas.common import Response, success
from app.schemas.audit_log import (
    AuditLogListRequest,
    AuditLogListResponse,
    AuditLogResponse,
    AuditAction,
    ResourceType,
)
from app.services.audit_log_service import AuditLogService

router = APIRouter()


@router.get(
    "/logs",
    response_model=Response[AuditLogListResponse],
    summary="获取审计日志列表",
    description="分页查询审计日志，支持按日期、用户、操作类型、资源类型筛选",
)
async def get_audit_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: int = Query(None, description="用户ID"),
    username: str = Query(None, description="用户名（模糊查询）"),
    action: str = Query(None, description="操作类型"),
    resource_type: str = Query(None, description="资源类型"),
    status: str = Query(None, description="操作结果：success/failure/error"),
    start_date: str = Query(None, description="开始日期（ISO格式）"),
    end_date: str = Query(None, description="结束日期（ISO格式）"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", description="排序方式：asc/desc"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取审计日志列表
    
    **权限要求：** audit:view
    
    **支持的筛选条件：**
    - user_id: 按用户ID筛选
    - username: 按用户名模糊查询
    - action: 按操作类型筛选
    - resource_type: 按资源类型筛选
    - status: 按操作结果筛选
    - start_date/end_date: 按日期范围筛选
    
    **支持的操作类型：**
    - login: 用户登录
    - logout: 用户登出
    - create_expense: 创建费用
    - update_expense: 更新费用
    - delete_expense: 删除费用
    - rebuild_kpi: 重建KPI
    - 等等...
    """
    # 检查权限
    await check_permission(current_user, "audit:view", db)
    
    # 构建请求
    from datetime import datetime
    
    request_data = AuditLogListRequest(
        page=page,
        page_size=page_size,
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        status=status,
        start_date=datetime.fromisoformat(start_date) if start_date else None,
        end_date=datetime.fromisoformat(end_date) if end_date else None,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    # 查询日志
    service = AuditLogService(db)
    result = await service.get_logs(request_data)
    
    return success(data=result)


@router.get(
    "/logs/{log_id}",
    response_model=Response[AuditLogResponse],
    summary="获取审计日志详情",
    description="根据ID获取单条审计日志的详细信息",
)
async def get_audit_log_detail(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取审计日志详情
    
    **权限要求：** audit:view
    """
    # 检查权限
    await check_permission(current_user, "audit:view", db)
    
    # 查询日志
    service = AuditLogService(db)
    log = await service.get_log_by_id(log_id)
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="审计日志不存在"
        )
    
    return success(data=AuditLogResponse.model_validate(log))


@router.get(
    "/actions",
    response_model=Response[List[str]],
    summary="获取所有操作类型",
    description="获取系统支持的所有审计操作类型列表",
)
async def get_audit_actions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有操作类型
    
    **权限要求：** audit:view
    """
    # 检查权限
    await check_permission(current_user, "audit:view", db)
    
    # 返回所有操作类型
    actions = [
        attr_value
        for attr_name, attr_value in vars(AuditAction).items()
        if not attr_name.startswith("_") and isinstance(attr_value, str)
    ]
    
    return success(data=actions)


@router.get(
    "/resource-types",
    response_model=Response[List[str]],
    summary="获取所有资源类型",
    description="获取系统支持的所有资源类型列表",
)
async def get_resource_types(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    获取所有资源类型
    
    **权限要求：** audit:view
    """
    # 检查权限
    await check_permission(current_user, "audit:view", db)
    
    # 返回所有资源类型
    resource_types = [
        attr_value
        for attr_name, attr_value in vars(ResourceType).items()
        if not attr_name.startswith("_") and isinstance(attr_value, str)
    ]
    
    return success(data=resource_types)
