"""
KPI 和审计日志模型

包含日指标汇总和审计日志
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint, Date, DateTime, ForeignKey, Integer, 
    Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class KpiDailyStore(Base, IDMixin, TimestampMixin):
    """
    门店日度 KPI 汇总模型
    
    存储每日门店的经营指标
    """
    
    __tablename__ = "kpi_daily_store"
    __table_args__ = (
        UniqueConstraint("biz_date", "store_id", name="uq_kpi_daily_store_date_store"),
        CheckConstraint("revenue >= 0", name="ck_kpi_daily_store_revenue"),
        CheckConstraint("net_revenue >= 0", name="ck_kpi_daily_store_net_revenue"),
        {"comment": "门店日度 KPI 汇总表"}
    )
    
    # 业务标识
    biz_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="业务日期"
    )
    
    store_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="门店ID"
    )
    
    # 营收指标
    revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="营业收入（gross）"
    )
    
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="退款金额"
    )
    
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="优惠金额"
    )
    
    net_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="净收入"
    )
    
    # 成本指标
    cost_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="总成本"
    )
    
    cost_material: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="原材料成本"
    )
    
    cost_labor: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="人工成本"
    )
    
    cost_rent: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="租金成本"
    )
    
    cost_utilities: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="水电煤成本"
    )
    
    cost_marketing: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="营销成本"
    )
    
    cost_other: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="其他成本"
    )
    
    # 利润指标
    gross_profit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="毛利润"
    )
    
    operating_profit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="营业利润"
    )
    
    profit_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        default=Decimal("0.0000"),
        comment="利润率"
    )
    
    # 订单指标
    order_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="订单数"
    )
    
    customer_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="客户数"
    )
    
    avg_order_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="客单价"
    )
    
    # 渠道分布
    dine_in_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="堂食收入"
    )
    
    takeout_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="外带收入"
    )
    
    delivery_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="外卖收入"
    )
    
    online_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="线上收入"
    )
    
    # 备注
    remark: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    store: Mapped["Store"] = relationship("Store")
    
    def __repr__(self) -> str:
        return f"<KpiDailyStore(id={self.id}, biz_date={self.biz_date}, store_id={self.store_id})>"


class AuditLog(Base, IDMixin):
    """
    审计日志模型
    
    记录系统关键操作日志
    """
    
    __tablename__ = "audit_log"
    __table_args__ = (
        {"comment": "审计日志表"}
    )
    
    # 用户信息
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="用户ID"
    )
    
    username: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="用户名（快照）"
    )
    
    # 操作信息
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="操作类型（create/update/delete/login/logout）"
    )
    
    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
        comment="资源类型"
    )
    
    resource_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="资源ID"
    )
    
    # 请求信息
    method: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="HTTP 方法"
    )
    
    path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="请求路径"
    )
    
    ip_address: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="IP 地址"
    )
    
    user_agent: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="User Agent"
    )
    
    # 详细信息（使用 PostgreSQL JSONB）
    detail: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="操作详情（JSON）"
    )
    
    # 结果信息
    status_code: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="响应状态码"
    )
    
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="错误信息"
    )
    
    # 时间信息
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        server_default="now()",
        comment="创建时间"
    )
    
    # 关联关系
    user: Mapped["User | None"] = relationship("User")
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource}')>"