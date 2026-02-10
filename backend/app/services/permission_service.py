"""
权限管理服务
"""

from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException
from app.models.user import Permission, role_permission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionService:
    """权限管理服务类"""

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 1000,
        search: Optional[str] = None,
        resource: Optional[str] = None
    ) -> tuple[List[Permission], int]:
        """
        获取权限列表

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            search: 搜索关键词
            resource: 资源类型

        Returns:
            (权限列表, 总数)
        """
        # 构建查询
        query = select(Permission)

        # 搜索条件
        if search:
            query = query.where(
                (Permission.name.contains(search)) |
                (Permission.code.contains(search))
            )

        # 资源过滤
        if resource:
            query = query.where(Permission.resource == resource)

        # 总数查询
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # 分页查询
        query = query.order_by(Permission.resource, Permission.action).offset(skip).limit(limit)
        result = await db.execute(query)
        permissions = result.scalars().all()

        return list(permissions), total

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Permission]:
        """
        获取所有权限（不分页）

        Args:
            db: 数据库会话

        Returns:
            权限列表
        """
        result = await db.execute(
            select(Permission).order_by(Permission.resource, Permission.action)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, permission_id: int) -> Permission:
        """
        根据ID获取权限

        Args:
            db: 数据库会话
            permission_id: 权限ID

        Returns:
            权限对象

        Raises:
            NotFoundException: 权限不存在
        """
        result = await db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        permission = result.scalar_one_or_none()

        if not permission:
            raise NotFoundException(f"权限 {permission_id} 不存在")

        return permission

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Permission]:
        """
        根据编码获取权限

        Args:
            db: 数据库会话
            code: 权限编码

        Returns:
            权限对象或None
        """
        result = await db.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: PermissionCreate) -> Permission:
        """
        创建权限

        Args:
            db: 数据库会话
            data: 权限创建数据

        Returns:
            创建的权限

        Raises:
            ConflictException: 权限编码已存在
        """
        # 检查编码是否已存在
        existing = await PermissionService.get_by_code(db, data.code)
        if existing:
            raise ConflictException(f"权限编码 {data.code} 已存在")

        # 创建权限
        permission = Permission(
            code=data.code,
            name=data.name,
            resource=data.resource,
            action=data.action,
            description=data.description
        )

        db.add(permission)
        await db.commit()
        await db.refresh(permission)

        return permission

    @staticmethod
    async def update(db: AsyncSession, permission_id: int, data: PermissionUpdate) -> Permission:
        """
        更新权限

        Args:
            db: 数据库会话
            permission_id: 权限ID
            data: 更新数据

        Returns:
            更新后的权限

        Raises:
            NotFoundException: 权限不存在
        """
        permission = await PermissionService.get_by_id(db, permission_id)

        # 更新字段
        if data.name is not None:
            permission.name = data.name
        if data.description is not None:
            permission.description = data.description

        await db.commit()
        await db.refresh(permission)

        return permission

    @staticmethod
    async def delete(db: AsyncSession, permission_id: int) -> None:
        """
        删除权限

        Args:
            db: 数据库会话
            permission_id: 权限ID

        Raises:
            NotFoundException: 权限不存在
        """
        permission = await PermissionService.get_by_id(db, permission_id)
        await db.delete(permission)
        await db.commit()

    @staticmethod
    async def get_resources(db: AsyncSession) -> List[str]:
        """
        获取所有资源类型

        Args:
            db: 数据库会话

        Returns:
            资源类型列表
        """
        result = await db.execute(
            select(Permission.resource).distinct().order_by(Permission.resource)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_permission_stats(db: AsyncSession, permission_id: int) -> dict:
        """
        获取权限统计信息

        Args:
            db: 数据库会话
            permission_id: 权限ID

        Returns:
            统计信息字典
        """
        # 角色数量
        role_count_result = await db.execute(
            select(func.count())
            .select_from(role_permission)
            .where(role_permission.c.permission_id == permission_id)
        )
        role_count = role_count_result.scalar_one()

        return {
            "role_count": role_count
        }
