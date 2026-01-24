"""
API 依赖项模块

提供常用的依赖注入函数，如数据库会话、当前用户等
"""

from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import verify_token
from app.models.user import User

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """获取当前认证用户"""
    token_data = verify_token(credentials.credentials)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 将 user_id 从字符串转换为整数
    try:
        user_id = int(token_data["sub"])
    except (ValueError, TypeError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def check_permission(
    user: User,
    permission_code: str,
    db: AsyncSession
) -> bool:
    """
    检查用户是否具有指定权限
    
    Args:
        user: 用户对象
        permission_code: 权限代码（如 audit:view）
        db: 数据库会话
        
    Returns:
        bool: 是否具有权限
        
    Raises:
        HTTPException: 没有权限时抛出403错误
    """
    from sqlalchemy.orm import selectinload
    from app.models.user import Permission
    
    # 超级用户拥有所有权限
    if user.is_superuser:
        return True
    
    # 加载用户的角色和权限
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.roles).selectinload(User.roles.property.mapper.class_.permissions)
        )
        .where(User.id == user.id)
    )
    user_with_perms = result.scalar_one_or_none()
    
    if not user_with_perms:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问"
        )
    
    # 检查权限
    has_permission = False
    for role in user_with_perms.roles:
        for perm in role.permissions:
            if perm.code == permission_code:
                has_permission = True
                break
        if has_permission:
            break
    
    if not has_permission:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"缺少所需权限: {permission_code}"
        )
    
    return True
