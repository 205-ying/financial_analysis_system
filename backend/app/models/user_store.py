"""
用户门店权限模型
用于控制用户能访问哪些门店的数据（数据权限）
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserStorePermission(Base):
    """
    用户门店权限表
    
    用于实现数据权限控制：
    - RBAC（角色权限）控制"能否访问某个功能"
    - 数据权限控制"能看哪些门店的数据"
    
    示例：
    - manager用户被授权访问门店A和门店B
    - 则该用户查询订单、费用、KPI时只能看到这两个门店的数据
    - admin用户无此限制（不存在记录时表示可访问全部）
    """
    __tablename__ = "user_store_permissions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("store.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 唯一约束：同一用户不能重复授权同一门店
    __table_args__ = (
        UniqueConstraint('user_id', 'store_id', name='uix_user_store'),
    )
    
    # 关联关系
    user = relationship("User", back_populates="store_permissions")
    store = relationship("Store")
