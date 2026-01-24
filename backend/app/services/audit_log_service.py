"""
审计日志服务

提供审计日志的创建、查询等功能
"""

import json
from datetime import datetime
from typing import Optional

from fastapi import Request
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogCreate, AuditLogListRequest, AuditLogListResponse, AuditLogResponse


class AuditLogService:
    """审计日志服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_log(
        self,
        action: str,
        username: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        detail: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None,
    ) -> AuditLog:
        """
        创建审计日志记录
        
        Args:
            action: 操作类型
            username: 操作用户名
            user_id: 操作用户ID
            resource_type: 资源类型
            resource_id: 资源ID
            detail: 操作详情（字典，会自动转为JSON）
            ip_address: 客户端IP
            user_agent: 客户端User-Agent
            status: 操作结果
            error_message: 错误信息
            
        Returns:
            创建的审计日志对象
        """
        # 过滤敏感信息
        if detail:
            detail = self._filter_sensitive_info(detail)
        
        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=json.dumps(detail, ensure_ascii=False) if detail else None,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            error_message=error_message,
        )
        
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        
        return audit_log
    
    async def get_logs(
        self,
        request: AuditLogListRequest,
    ) -> AuditLogListResponse:
        """
        查询审计日志列表
        
        Args:
            request: 查询请求参数
            
        Returns:
            分页的日志列表
        """
        # 构建查询条件
        conditions = []
        
        if request.user_id:
            conditions.append(AuditLog.user_id == request.user_id)
        
        if request.username:
            conditions.append(AuditLog.username.ilike(f"%{request.username}%"))
        
        if request.action:
            conditions.append(AuditLog.action == request.action)
        
        if request.resource_type:
            conditions.append(AuditLog.resource_type == request.resource_type)
        
        if request.status:
            conditions.append(AuditLog.status == request.status)
        
        if request.start_date:
            conditions.append(AuditLog.created_at >= request.start_date)
        
        if request.end_date:
            conditions.append(AuditLog.created_at <= request.end_date)
        
        # 构建查询
        query = select(AuditLog)
        if conditions:
            query = query.where(and_(*conditions))
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        total = result.scalar_one()
        
        # 排序
        sort_column = getattr(AuditLog, request.sort_by, AuditLog.created_at)
        if request.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # 分页
        offset = (request.page - 1) * request.page_size
        query = query.offset(offset).limit(request.page_size)
        
        # 执行查询
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        # 计算总页数
        total_pages = (total + request.page_size - 1) // request.page_size
        
        return AuditLogListResponse(
            total=total,
            page=request.page,
            page_size=request.page_size,
            total_pages=total_pages,
            items=[AuditLogResponse.model_validate(log) for log in logs],
        )
    
    async def get_log_by_id(self, log_id: int) -> Optional[AuditLog]:
        """
        根据ID获取审计日志
        
        Args:
            log_id: 日志ID
            
        Returns:
            审计日志对象，如果不存在则返回None
        """
        result = await self.db.execute(
            select(AuditLog).where(AuditLog.id == log_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    def _filter_sensitive_info(detail: dict) -> dict:
        """
        过滤敏感信息
        
        Args:
            detail: 原始详情字典
            
        Returns:
            过滤后的字典
        """
        sensitive_keys = [
            "password",
            "password_hash",
            "hashed_password",
            "token",
            "access_token",
            "refresh_token",
            "secret",
            "api_key",
            "private_key",
        ]
        
        filtered = {}
        for key, value in detail.items():
            # 检查键名是否包含敏感词
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                filtered[key] = "***FILTERED***"
            elif isinstance(value, dict):
                # 递归过滤嵌套字典
                filtered[key] = AuditLogService._filter_sensitive_info(value)
            else:
                filtered[key] = value
        
        return filtered
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        获取客户端IP地址
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            客户端IP地址
        """
        # 优先从 X-Forwarded-For 获取（考虑代理/负载均衡）
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # 其次从 X-Real-IP 获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 最后使用直连IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    @staticmethod
    def get_user_agent(request: Request) -> str:
        """
        获取客户端User-Agent
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            User-Agent字符串
        """
        return request.headers.get("User-Agent", "unknown")


# 便捷函数：用于在路由中快速记录审计日志
async def log_audit(
    db: AsyncSession,
    action: str,
    user: User,
    request: Request,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    detail: Optional[dict] = None,
    status: str = "success",
    error_message: Optional[str] = None,
) -> AuditLog:
    """
    记录审计日志的便捷函数
    
    Args:
        db: 数据库会话
        action: 操作类型
        user: 当前用户对象
        request: FastAPI请求对象
        resource_type: 资源类型
        resource_id: 资源ID
        detail: 操作详情
        status: 操作结果
        error_message: 错误信息
        
    Returns:
        创建的审计日志对象
    """
    service = AuditLogService(db)
    
    return await service.create_log(
        action=action,
        username=user.username,
        user_id=user.id,
        resource_type=resource_type,
        resource_id=resource_id,
        detail=detail,
        ip_address=service.get_client_ip(request),
        user_agent=service.get_user_agent(request),
        status=status,
        error_message=error_message,
    )
