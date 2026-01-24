"""
审计日志模型

记录系统关键操作的审计日志，用于安全审计和问题追踪
"""

from __future__ import annotations

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class AuditLog(Base, IDMixin, TimestampMixin):
    """
    审计日志模型
    
    记录用户的关键操作，包括登录、数据修改等
    支持按用户、操作类型、资源类型等维度查询
    """
    
    __tablename__ = "audit_log"
    __table_args__ = (
        Index("ix_audit_log_user_id", "user_id"),
        Index("ix_audit_log_action", "action"),
        Index("ix_audit_log_resource_type", "resource_type"),
        Index("ix_audit_log_created_at", "created_at"),
        {"comment": "审计日志表", "extend_existing": True}
    )
    
    # 用户信息
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="操作用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="操作用户名（冗余存储，防止用户删除后无法追溯）"
    )
    
    # 操作信息
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="操作类型：login/logout/create_expense/update_expense/delete_expense/rebuild_kpi等"
    )
    
    # 资源信息
    resource_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="资源类型：expense/kpi/order/store/user等"
    )
    resource_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="资源ID"
    )
    
    # 详细信息
    detail: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="操作详情（JSON格式），不包含敏感信息如密码"
    )
    
    # 请求信息
    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
        comment="客户端IP地址（支持IPv6）"
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="客户端User-Agent"
    )
    
    # 结果信息
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="success",
        comment="操作结果：success/failure/error"
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="错误信息（仅在失败时记录）"
    )
    
    # 关联关系
    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], lazy="selectin")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, username={self.username}, status={self.status})>"
