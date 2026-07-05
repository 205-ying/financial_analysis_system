"""
KPI 和审计日志模型

包含日指标汇总和审计日志
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.store import Store


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
        {"comment": "门店日度 KPI 汇总表"},
    )

    # 业务标识
    biz_date: Mapped[date] = mapped_column(
        Date, nullable=False, index=True, comment="业务日期"
    )

    store_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="门店ID",
    )

    # 营收指标
    revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="营业收入（gross）",
    )

    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="退款金额"
    )

    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="优惠金额"
    )

    net_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="净收入"
    )

    # 成本指标
    cost_total: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="总成本"
    )

    cost_material: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="原材料成本"
    )

    cost_labor: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="人工成本"
    )

    cost_rent: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="租金成本"
    )

    cost_utilities: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="水电煤成本"
    )

    cost_marketing: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="营销成本"
    )

    cost_other: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="其他成本"
    )

    # 利润指标
    gross_profit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="毛利润"
    )

    operating_profit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="营业利润"
    )

    profit_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), nullable=False, default=Decimal("0.0000"), comment="利润率"
    )

    # 订单指标
    order_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="订单数"
    )

    customer_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="客户数"
    )

    avg_order_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=Decimal("0.00"), comment="客单价"
    )

    # 渠道分布
    dine_in_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="堂食收入"
    )

    takeout_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="外带收入"
    )

    delivery_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="外卖收入"
    )

    online_revenue: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00"), comment="线上收入"
    )

    # 备注
    remark: Mapped[str | None] = mapped_column(Text, nullable=True, comment="备注")

    # 关联关系
    store: Mapped[Store] = relationship("Store")

    def __repr__(self) -> str:
        return f"<KpiDailyStore(id={self.id}, biz_date={self.biz_date}, store_id={self.store_id})>"
