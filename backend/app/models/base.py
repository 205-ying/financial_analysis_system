"""
数据库模型基础类

提供常用的 Mixin 类，包含 ID、时间戳、软删除、用户追踪等功能
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, DateTime, Boolean, String, ForeignKey, func, Uuid
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.ext.declarative import declared_attr

# 创建基础模型类
Base = declarative_base()


class IDMixin:
    """ID 主键 Mixin"""
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")


class UUIDMixin:
    """UUID 主键 Mixin"""
    id = Column(Uuid, primary_key=True, default=uuid.uuid4, index=True, comment="主键UUID")


class TimestampMixin:
    """时间戳 Mixin"""
    created_at = Column(
        DateTime,
        default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )


class SoftDeleteMixin:
    """软删除 Mixin"""
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否已删除")
    deleted_at = Column(DateTime, nullable=True, comment="删除时间")
    
    def soft_delete(self):
        """标记为软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self):
        """恢复软删除"""
        self.is_deleted = False
        self.deleted_at = None


class UserTrackingMixin:
    """用户追踪 Mixin - 记录创建和更新的用户"""
    
    @declared_attr
    def created_by_id(cls):
        return Column(Integer, ForeignKey("users.id"), nullable=True, comment="创建用户ID")
    
    @declared_attr
    def updated_by_id(cls):
        return Column(Integer, ForeignKey("users.id"), nullable=True, comment="更新用户ID")
    
    @declared_attr
    def created_by(cls):
        return relationship("User", foreign_keys=[cls.created_by_id])
    
    @declared_attr
    def updated_by(cls):
        return relationship("User", foreign_keys=[cls.updated_by_id])


class BaseModel(Base, IDMixin, TimestampMixin):
    """基础模型类 - 包含 ID 和时间戳"""
    __abstract__ = True


class BaseModelWithSoftDelete(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    """带软删除的基础模型类"""
    __abstract__ = True


class BaseModelWithUserTracking(Base, IDMixin, TimestampMixin, UserTrackingMixin):
    """带用户追踪的基础模型类"""
    __abstract__ = True


class FullBaseModel(Base, IDMixin, TimestampMixin, SoftDeleteMixin, UserTrackingMixin):
    """完整功能的基础模型类 - 包含所有 Mixin"""
    __abstract__ = True


# 常用状态枚举
class StatusEnum:
    """通用状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"
    DELETED = "deleted"


class OrderStatusEnum:
    """订单状态枚举"""
    PENDING = "pending"          # 待处理
    CONFIRMED = "confirmed"      # 已确认
    PREPARING = "preparing"      # 制作中
    READY = "ready"             # 待取餐
    DELIVERED = "delivered"      # 已送达
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消
    REFUNDED = "refunded"       # 已退款


class PaymentStatusEnum:
    """支付状态枚举"""
    PENDING = "pending"          # 待支付
    PAID = "paid"               # 已支付
    FAILED = "failed"           # 支付失败
    REFUNDED = "refunded"       # 已退款
    CANCELLED = "cancelled"     # 已取消