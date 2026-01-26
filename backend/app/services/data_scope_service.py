"""
数据权限服务
用于控制用户能访问哪些门店的数据
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.user_store import UserStorePermission
from app.core.exceptions import AuthorizationException


async def get_accessible_store_ids(db: AsyncSession, user: User) -> Optional[List[int]]:
    """
    获取用户可访问的门店ID列表
    
    Args:
        db: 数据库会话
        user: 用户对象
        
    Returns:
        - None: 表示可访问全部门店（超级管理员/没有门店限制）
        - List[int]: 可访问的门店ID列表
        
    规则：
    - 超级管理员：返回 None（可访问全部）
    - 没有门店权限记录：返回 None（可访问全部，向后兼容）
    - 有门店权限记录：返回授权的门店ID列表
    """
    # 超级管理员可访问全部门店
    if user.is_superuser:
        return None
    
    # 查询用户的门店权限
    result = await db.execute(
        select(UserStorePermission.store_id)
        .where(UserStorePermission.user_id == user.id)
    )
    store_ids = [row[0] for row in result.all()]
    
    # 如果没有门店权限记录，返回 None（可访问全部，向后兼容）
    # 这样已有系统升级后不会影响现有用户
    if not store_ids:
        return None
    
    return store_ids


async def assert_store_access(
    db: AsyncSession, 
    user: User, 
    store_id: int
) -> None:
    """
    断言用户有权访问指定门店，无权限时抛出异常
    
    Args:
        db: 数据库会话
        user: 用户对象
        store_id: 门店ID
        
    Raises:
        AuthorizationException: 当用户无权访问该门店时抛出
        
    使用场景：
    - 订单详情查询（明确指定了门店ID）
    - 费用记录详情查询
    - KPI重建（指定门店）
    """
    # 获取可访问的门店列表
    accessible_store_ids = await get_accessible_store_ids(db, user)
    
    # None 表示可访问全部门店
    if accessible_store_ids is None:
        return
    
    # 检查指定门店是否在可访问列表中
    if store_id not in accessible_store_ids:
        raise AuthorizationException(
            f"您无权访问门店ID={store_id}的数据。"
            f"当前您仅有权访问门店ID: {', '.join(map(str, accessible_store_ids))}"
        )


async def filter_stores_by_access(
    db: AsyncSession,
    user: User,
    requested_store_id: Optional[int] = None
) -> Optional[List[int]]:
    """
    根据用户权限过滤门店ID，用于列表查询
    
    Args:
        db: 数据库会话
        user: 用户对象
        requested_store_id: 请求的门店ID（来自查询参数）
        
    Returns:
        - None: 不限制门店（超级管理员或无限制用户）
        - List[int]: 限制在指定的门店列表中
        
    Raises:
        AuthorizationException: 当请求的门店ID不在可访问范围内时抛出
        
    使用场景：
    - 订单列表查询
    - 费用列表查询
    - KPI查询
    - 报表查询
    """
    # 获取用户可访问的门店列表
    accessible_store_ids = await get_accessible_store_ids(db, user)
    
    # 如果用户可访问全部门店
    if accessible_store_ids is None:
        # 如果请求指定了门店，返回该门店（单门店过滤）
        if requested_store_id is not None:
            return [requested_store_id]
        # 否则不限制
        return None
    
    # 用户有门店限制
    if requested_store_id is not None:
        # 检查请求的门店是否在可访问列表中
        if requested_store_id not in accessible_store_ids:
            raise AuthorizationException(
                f"您无权访问门店ID={requested_store_id}的数据。"
                f"当前您仅有权访问门店ID: {', '.join(map(str, accessible_store_ids))}"
            )
        # 返回请求的单个门店
        return [requested_store_id]
    
    # 未指定门店，返回用户可访问的全部门店列表
    return accessible_store_ids
