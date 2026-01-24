"""
依赖注入：认证和权限校验
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, Role, Permission


# HTTP Bearer Token 安全方案
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """
    获取当前登录用户
    
    依赖注入函数，用于需要认证的接口
    从 JWT token 中解析用户信息并从数据库加载完整用户对象
    
    Args:
        credentials: Bearer Token
        db: 数据库会话
        
    Returns:
        User: 当前用户对象（包含 roles 和 permissions）
        
    Raises:
        HTTPException: 401 Unauthorized
    """
    # 解码 JWT token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从 payload 中获取 user_id
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 从数据库加载用户（预加载 roles 和 permissions）
    stmt = (
        select(User)
        .options(
            selectinload(User.roles).selectinload(Role.permissions)
        )
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    获取当前活跃用户（已激活且未删除）
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 当前活跃用户
        
    Raises:
        HTTPException: 403 Forbidden
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户未激活"
        )
    
    return current_user


def require_permissions(required_perms: list[str]):
    """
    权限校验装饰器工厂
    
    创建一个依赖函数，用于检查用户是否拥有所需权限
    
    Args:
        required_perms: 所需权限列表，例如 ["order:view", "order:create"]
        
    Returns:
        依赖函数
        
    Usage:
        ```python
        @router.get("/orders")
        async def list_orders(
            user: Annotated[User, Depends(require_permissions(["order:view"]))]
        ):
            ...
        ```
    """
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ) -> User:
        """
        检查用户权限
        
        Args:
            current_user: 当前用户
            
        Returns:
            User: 有权限的用户
            
        Raises:
            HTTPException: 403 Forbidden
        """
        # 超级用户拥有所有权限
        if current_user.is_superuser:
            return current_user
        
        # 获取用户所有权限
        user_permissions = set()
        for role in current_user.roles:
            for perm in role.permissions:
                user_permissions.add(perm.code)
        
        # 检查是否拥有所需权限
        for required_perm in required_perms:
            if required_perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"权限不足：需要 {required_perm} 权限"
                )
        
        return current_user
    
    return permission_checker


def require_superuser(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    要求超级管理员权限
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 超级管理员用户
        
    Raises:
        HTTPException: 403 Forbidden
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    
    return current_user


# 类型别名，简化使用
CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveUser = Annotated[User, Depends(get_current_active_user)]
SuperUser = Annotated[User, Depends(require_superuser)]
