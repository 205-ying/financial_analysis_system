"""
角色管理服务
"""

from typing import List, Optional
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ConflictException, ValidationException
from app.core.security import hash_password
from app.models.user import Role, Permission, role_permission, User, user_role
from app.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    """角色管理服务类"""

    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[Role], int]:
        """
        获取角色列表

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数
            search: 搜索关键词（名称或编码）
            is_active: 是否启用

        Returns:
            (角色列表, 总数)
        """
        # 构建查询
        query = select(Role).options(selectinload(Role.permissions))

        # 搜索条件
        if search:
            query = query.where(
                (Role.name.contains(search)) | (Role.code.contains(search))
            )

        # 状态过滤
        if is_active is not None:
            query = query.where(Role.is_active == is_active)

        # 总数查询
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # 分页查询
        query = query.order_by(Role.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        roles = result.scalars().all()

        return list(roles), total

    @staticmethod
    async def get_by_id(db: AsyncSession, role_id: int) -> Role:
        """
        根据ID获取角色

        Args:
            db: 数据库会话
            role_id: 角色ID

        Returns:
            角色对象

        Raises:
            NotFoundException: 角色不存在
        """
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        role = result.scalar_one_or_none()

        if not role:
            raise NotFoundException(f"角色 {role_id} 不存在")

        return role

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Role]:
        """
        根据编码获取角色

        Args:
            db: 数据库会话
            code: 角色编码

        Returns:
            角色对象或None
        """
        result = await db.execute(
            select(Role).where(Role.code == code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: RoleCreate) -> Role:
        """
        创建角色

        Args:
            db: 数据库会话
            data: 角色创建数据

        Returns:
            创建的角色

        Raises:
            ConflictException: 角色编码已存在
        """
        # 检查编码是否已存在
        existing = await RoleService.get_by_code(db, data.code)
        if existing:
            raise ConflictException(f"角色编码 {data.code} 已存在")

        # 创建角色
        role = Role(
            code=data.code,
            name=data.name,
            description=data.description,
            is_active=data.is_active
        )

        # 分配权限
        if data.permission_ids:
            permissions_result = await db.execute(
                select(Permission).where(Permission.id.in_(data.permission_ids))
            )
            permissions = permissions_result.scalars().all()
            role.permissions = list(permissions)

        db.add(role)
        await db.commit()
        await db.refresh(role)

        return role

    @staticmethod
    async def update(db: AsyncSession, role_id: int, data: RoleUpdate) -> Role:
        """
        更新角色

        Args:
            db: 数据库会话
            role_id: 角色ID
            data: 更新数据

        Returns:
            更新后的角色

        Raises:
            NotFoundException: 角色不存在
        """
        role = await RoleService.get_by_id(db, role_id)

        # 更新字段
        if data.name is not None:
            role.name = data.name
        if data.description is not None:
            role.description = data.description
        if data.is_active is not None:
            role.is_active = data.is_active

        await db.commit()
        await db.refresh(role)

        return role

    @staticmethod
    async def delete(db: AsyncSession, role_id: int) -> None:
        """
        删除角色

        Args:
            db: 数据库会话
            role_id: 角色ID

        Raises:
            NotFoundException: 角色不存在
            ValidationException: 角色仍有用户
        """
        role = await RoleService.get_by_id(db, role_id)

        # 检查是否有用户使用该角色
        user_count_result = await db.execute(
            select(func.count())
            .select_from(user_role)
            .where(user_role.c.role_id == role_id)
        )
        user_count = user_count_result.scalar_one()

        if user_count > 0:
            raise ValidationException(f"角色 {role.name} 仍有 {user_count} 个用户，无法删除")

        await db.delete(role)
        await db.commit()

    @staticmethod
    async def assign_permissions(
        db: AsyncSession,
        role_id: int,
        permission_ids: List[int]
    ) -> Role:
        """
        为角色分配权限

        Args:
            db: 数据库会话
            role_id: 角色ID
            permission_ids: 权限ID列表

        Returns:
            更新后的角色

        Raises:
            NotFoundException: 角色不存在
        """
        role = await RoleService.get_by_id(db, role_id)

        # 查询新的权限列表
        if permission_ids:
            permissions_result = await db.execute(
                select(Permission).where(Permission.id.in_(permission_ids))
            )
            new_permissions = list(permissions_result.scalars().all())
        else:
            new_permissions = []

        # 直接通过 ORM relationship 替换权限（不要混用 delete + relationship）
        role.permissions = new_permissions

        await db.commit()

        # 重新加载角色及权限关系
        result = await db.execute(
            select(Role)
            .options(selectinload(Role.permissions))
            .where(Role.id == role_id)
        )
        role = result.scalar_one()

        return role

    @staticmethod
    async def get_role_stats(db: AsyncSession, role_id: int) -> dict:
        """
        获取角色统计信息

        Args:
            db: 数据库会话
            role_id: 角色ID

        Returns:
            统计信息字典
        """
        # 用户数量
        user_count_result = await db.execute(
            select(func.count())
            .select_from(user_role)
            .where(user_role.c.role_id == role_id)
        )
        user_count = user_count_result.scalar_one()

        # 权限数量
        permission_count_result = await db.execute(
            select(func.count())
            .select_from(role_permission)
            .where(role_permission.c.role_id == role_id)
        )
        permission_count = permission_count_result.scalar_one()

        return {
            "user_count": user_count,
            "permission_count": permission_count
        }

    @staticmethod
    async def get_user_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[User], int]:
        """获取用户列表（含角色）"""
        query = select(User).options(selectinload(User.roles))

        if search:
            query = query.where(
                (User.username.contains(search))
                | (User.full_name.contains(search))
                | (User.phone.contains(search))
            )

        if is_active is not None:
            query = query.where(User.is_active == is_active)

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()

        return list(users), total

    @staticmethod
    async def get_user_with_roles(db: AsyncSession, user_id: int) -> User:
        """按ID获取用户及其角色"""
        result = await db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException(f"用户 {user_id} 不存在")

        return user

    @staticmethod
    async def assign_roles_to_user(
        db: AsyncSession,
        user_id: int,
        role_ids: List[int],
    ) -> User:
        """为用户分配角色（覆盖式保存）"""
        user = await RoleService.get_user_with_roles(db, user_id)

        deduplicated_role_ids = list(dict.fromkeys(role_ids))

        if deduplicated_role_ids:
            roles_result = await db.execute(
                select(Role).where(Role.id.in_(deduplicated_role_ids))
            )
            roles = list(roles_result.scalars().all())

            found_role_ids = {role.id for role in roles}
            missing_role_ids = [role_id for role_id in deduplicated_role_ids if role_id not in found_role_ids]
            if missing_role_ids:
                raise NotFoundException(f"角色不存在: {', '.join(map(str, missing_role_ids))}")
        else:
            roles = []

        user.roles = roles
        await db.commit()

        return await RoleService.get_user_with_roles(db, user_id)

    @staticmethod
    async def create_user(
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        is_active: bool = True,
    ) -> User:
        """创建用户"""
        username_clean = username.strip()
        email_clean = email.strip().lower()

        existing_username = await db.execute(
            select(User).where(User.username == username_clean)
        )
        if existing_username.scalar_one_or_none() is not None:
            raise ConflictException(f"用户名 {username_clean} 已存在")

        existing_email = await db.execute(
            select(User).where(User.email == email_clean)
        )
        if existing_email.scalar_one_or_none() is not None:
            raise ConflictException(f"邮箱 {email_clean} 已存在")

        user = User(
            username=username_clean,
            email=email_clean,
            password_hash=hash_password(password),
            full_name=full_name.strip() if full_name else None,
            phone=phone.strip() if phone else None,
            is_active=is_active,
            is_superuser=False,
        )

        db.add(user)
        await db.commit()

        return await RoleService.get_user_with_roles(db, user.id)

    @staticmethod
    async def update_user_basic_info(
        db: AsyncSession,
        user_id: int,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> User:
        """更新用户基础信息（不含角色、密码）"""
        user = await RoleService.get_user_with_roles(db, user_id)

        if email is not None:
            email_clean = email.strip().lower()
            existing_email = await db.execute(
                select(User).where(User.email == email_clean, User.id != user_id)
            )
            if existing_email.scalar_one_or_none() is not None:
                raise ConflictException(f"邮箱 {email_clean} 已存在")
            user.email = email_clean

        if full_name is not None:
            user.full_name = full_name.strip() or None

        if phone is not None:
            user.phone = phone.strip() or None

        await db.commit()

        return await RoleService.get_user_with_roles(db, user_id)

    @staticmethod
    async def update_user_status(
        db: AsyncSession,
        user_id: int,
        is_active: bool,
    ) -> User:
        """更新用户启用状态"""
        user = await RoleService.get_user_with_roles(db, user_id)
        user.is_active = is_active
        await db.commit()

        return await RoleService.get_user_with_roles(db, user_id)
