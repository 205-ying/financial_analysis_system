"""
审计日志服务
"""

from datetime import datetime
from typing import Any, Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User


async def create_audit_log(
    db: AsyncSession,
    user: Optional[User],
    action: str,
    resource: str,
    resource_id: Optional[str] = None,
    detail: Optional[dict[str, Any]] = None,
    request: Optional[Request] = None,
    status_code: Optional[int] = None,
    error_message: Optional[str] = None
) -> AuditLog:
    """
    创建审计日志
    
    Args:
        db: 数据库会话
        user: 操作用户（可选，匿名操作传 None）
        action: 操作类型（CREATE/UPDATE/DELETE/LOGIN/LOGOUT/EXPORT等）
        resource: 资源类型（user/store/order/expense/kpi等）
        resource_id: 资源ID（可选）
        detail: 操作详情（JSONB格式，自动过滤敏感字段）
        request: FastAPI Request 对象（用于提取 IP、UA、路径）
        status_code: HTTP 状态码
        error_message: 错误信息（操作失败时）
        
    Returns:
        AuditLog: 创建的审计日志对象
        
    Examples:
        ```python
        # 记录用户登录
        await create_audit_log(
            db=db,
            user=user,
            action="LOGIN",
            resource="user",
            resource_id=str(user.id),
            request=request,
            status_code=200
        )
        
        # 记录订单创建
        await create_audit_log(
            db=db,
            user=current_user,
            action="CREATE",
            resource="order",
            resource_id=order.order_no,
            detail={
                "store_id": order.store_id,
                "total_amount": float(order.net_amount),
                "items_count": len(order.items)
            },
            request=request,
            status_code=201
        )
        ```
    """
    # 过滤敏感字段
    if detail:
        detail = _filter_sensitive_data(detail)
    
    # 提取请求信息
    ip_address = None
    user_agent = None
    method = None
    path = None
    
    if request:
        # 获取真实 IP（考虑代理）
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip_address = forwarded.split(",")[0].strip()
        else:
            ip_address = request.client.host if request.client else None
        
        user_agent = request.headers.get("User-Agent")
        method = request.method
        path = str(request.url.path)
    
    # 创建审计日志
    audit_log = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "匿名",
        action=action,
        resource_type=resource,
        resource_id=int(resource_id) if resource_id and resource_id.isdigit() else None,
        detail=str(detail) if detail else None,
        ip_address=ip_address,
        user_agent=user_agent,
        status="success" if status_code and 200 <= status_code < 300 else "failure",
        error_message=error_message
    )
    
    db.add(audit_log)
    await db.flush()
    
    return audit_log


def _filter_sensitive_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    过滤敏感数据
    
    移除密码、令牌等敏感字段
    
    Args:
        data: 原始数据
        
    Returns:
        dict: 过滤后的数据
    """
    sensitive_keys = {
        "password",
        "password_hash",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "api_key",
        "private_key",
        "credential"
    }
    
    filtered = {}
    for key, value in data.items():
        # 跳过敏感字段
        if key.lower() in sensitive_keys:
            filtered[key] = "***FILTERED***"
        # 递归处理嵌套字典
        elif isinstance(value, dict):
            filtered[key] = _filter_sensitive_data(value)
        # 递归处理列表
        elif isinstance(value, list):
            filtered[key] = [
                _filter_sensitive_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            filtered[key] = value
    
    return filtered


async def log_operation(
    db: AsyncSession,
    user: User,
    action: str,
    resource: str,
    resource_id: str,
    detail: dict[str, Any],
    request: Request
) -> None:
    """
    便捷函数：记录成功的操作
    
    Args:
        db: 数据库会话
        user: 操作用户
        action: 操作类型
        resource: 资源类型
        resource_id: 资源ID
        detail: 操作详情
        request: FastAPI Request
    """
    await create_audit_log(
        db=db,
        user=user,
        action=action,
        resource=resource,
        resource_id=resource_id,
        detail=detail,
        request=request,
        status_code=200
    )


async def log_error(
    db: AsyncSession,
    user: Optional[User],
    action: str,
    resource: str,
    error_message: str,
    request: Request,
    status_code: int = 500
) -> None:
    """
    便捷函数：记录失败的操作
    
    Args:
        db: 数据库会话
        user: 操作用户
        action: 操作类型
        resource: 资源类型
        error_message: 错误信息
        request: FastAPI Request
        status_code: HTTP 状态码
    """
    await create_audit_log(
        db=db,
        user=user,
        action=action,
        resource=resource,
        error_message=error_message,
        request=request,
        status_code=status_code
    )
