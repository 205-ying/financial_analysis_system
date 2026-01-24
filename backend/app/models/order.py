"""
订单模型

包含订单主表和明细表
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class OrderHeader(Base, IDMixin, TimestampMixin):
    """
    订单主表
    
    存储订单汇总信息
    """
    
    __tablename__ = "order_header"
    __table_args__ = (
        UniqueConstraint("order_no", name="uq_order_header_order_no"),
        CheckConstraint("gross_amount >= 0", name="ck_order_header_gross_amount"),
        CheckConstraint("discount_amount >= 0", name="ck_order_header_discount_amount"),
        CheckConstraint("net_amount >= 0", name="ck_order_header_net_amount"),
        {"comment": "订单主表"}
    )
    
    # 订单基本信息
    order_no: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="订单号"
    )
    
    store_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="门店ID"
    )
    
    biz_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="业务日期"
    )
    
    order_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="下单时间"
    )
    
    # 渠道信息
    channel: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="订单渠道（dine_in/takeout/delivery/online）"
    )
    
    table_no: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="桌号"
    )
    
    # 金额信息
    gross_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="商品总额"
    )
    
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="优惠金额"
    )
    
    service_charge: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="服务费"
    )
    
    delivery_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="配送费"
    )
    
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="实收金额"
    )
    
    # 支付信息
    payment_method: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="支付方式（cash/alipay/wechat/card/other）"
    )
    
    payment_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="支付时间"
    )
    
    # 订单状态
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
        comment="订单状态（pending/confirmed/preparing/completed/cancelled/refunded）"
    )
    
    # 客户信息
    customer_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="客户姓名"
    )
    
    customer_phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="客户电话"
    )
    
    customer_address: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="客户地址"
    )
    
    # 其他信息
    remark: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="订单备注"
    )
    
    # 操作人员
    operator_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="操作员ID"
    )
    
    # 关联关系
    store: Mapped["Store"] = relationship("Store")
    operator: Mapped["User | None"] = relationship("User")
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<OrderHeader(id={self.id}, order_no='{self.order_no}', status='{self.status}')>"


class OrderItem(Base, IDMixin, TimestampMixin):
    """
    订单明细表
    
    存储订单商品明细信息
    """
    
    __tablename__ = "order_item"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_item_quantity"),
        CheckConstraint("unit_price >= 0", name="ck_order_item_unit_price"),
        CheckConstraint("line_amount >= 0", name="ck_order_item_line_amount"),
        {"comment": "订单明细表"}
    )
    
    # 订单关联
    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("order_header.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="订单ID"
    )
    
    # 产品信息（使用快照）
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="产品ID"
    )
    
    # 产品快照字段（记录下单时的产品信息）
    product_sku: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="产品SKU（快照）"
    )
    
    product_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="产品名称（快照）"
    )
    
    product_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="产品分类（快照）"
    )
    
    # 数量和价格
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3),
        nullable=False,
        comment="数量"
    )
    
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="份",
        comment="单位"
    )
    
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="单价"
    )
    
    line_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="小计金额"
    )
    
    # 折扣信息
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="优惠金额"
    )
    
    # 备注
    remark: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="商品备注"
    )
    
    # 关联关系
    order: Mapped["OrderHeader"] = relationship(
        "OrderHeader",
        back_populates="items"
    )
    
    product: Mapped["Product"] = relationship("Product")
    
    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, order_id={self.order_id}, product_name='{self.product_name}')>"