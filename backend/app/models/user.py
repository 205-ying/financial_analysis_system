"""
用户认证和权限模型

包含用户、角色、权限及其关联关系
"""

from __future__ import annotations

from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


# 用户-角色关联表（多对多）
user_role = Table(
    "user_role",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    comment="用户角色关联表"
)


# 角色-权限关联表（多对多）
role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
    comment="角色权限关联表"
)


class User(Base, IDMixin, TimestampMixin):
    """
    用户模型
    
    存储系统用户信息，包括认证和基本信息
    """
    
    __tablename__ = "user"
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
        UniqueConstraint("email", name="uq_user_email"),
        {"comment": "用户表"}
    )
    
    # 基本信息
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="用户名"
    )
    
    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="邮箱"
    )
    
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    
    full_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="真实姓名"
    )
    
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="手机号"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否激活"
    )
    
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否超级用户"
    )
    
    # 关联关系
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        secondary=user_role,
        back_populates="users",
        lazy="selectin"
    )
    
    # 门店数据权限
    store_permissions: Mapped[List["UserStorePermission"]] = relationship(
        "UserStorePermission",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"


class Role(Base, IDMixin, TimestampMixin):
    """
    角色模型
    
    定义系统角色及其权限
    """
    
    __tablename__ = "role"
    __table_args__ = (
        UniqueConstraint("code", name="uq_role_code"),
        {"comment": "角色表"}
    )
    
    # 基本信息
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="角色编码"
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="角色名称"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="角色描述"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用"
    )
    
    # 关联关系
    users: Mapped[List["User"]] = relationship(
        secondary=user_role,
        back_populates="roles"
    )
    
    permissions: Mapped[List["Permission"]] = relationship(
        secondary=role_permission,
        back_populates="roles",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, code='{self.code}', name='{self.name}')>"


class Permission(Base, IDMixin, TimestampMixin):
    """
    权限模型
    
    定义系统权限点
    """
    
    __tablename__ = "permission"
    __table_args__ = (
        UniqueConstraint("code", name="uq_permission_code"),
        {"comment": "权限表"}
    )
    
    # 基本信息
    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="权限编码"
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="权限名称"
    )
    
    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="资源标识"
    )
    
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="操作类型"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="权限描述"
    )
    
    # 关联关系
    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permission,
        back_populates="permissions"
    )
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, code='{self.code}', resource='{self.resource}', action='{self.action}')>"