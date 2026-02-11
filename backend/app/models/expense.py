"""
费用管理模型

包含费用科目和费用记录
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin, SoftDeleteMixin


class ExpenseType(Base, IDMixin, TimestampMixin):
    """
    费用科目模型
    
    支持树形结构的费用分类
    """
    
    __tablename__ = "expense_type"
    __table_args__ = (
        UniqueConstraint("type_code", name="uq_expense_type_code"),
        {"comment": "费用科目表"}
    )
    
    # 基本信息
    type_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="费用科目编码"
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="费用科目名称"
    )
    
    # 树形结构
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("expense_type.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="父科目ID"
    )
    
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="科目层级"
    )
    
    # 科目属性
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="费用类别（operating/marketing/administrative/other）"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="科目描述"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否启用"
    )
    
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序顺序"
    )
    
    # CVP 分析相关
    cost_behavior: Mapped[str] = mapped_column(
        String(20),
        default="variable",
        nullable=False,
        comment="成本习性（fixed=固定成本, variable=变动成本）"
    )
    
    # 关联关系
    parent: Mapped["ExpenseType | None"] = relationship(
        "ExpenseType",
        remote_side="ExpenseType.id",
        back_populates="children"
    )
    
    children: Mapped[List["ExpenseType"]] = relationship(
        "ExpenseType",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
    records: Mapped[List["ExpenseRecord"]] = relationship(
        "ExpenseRecord",
        back_populates="expense_type"
    )
    
    def __repr__(self) -> str:
        return f"<ExpenseType(id={self.id}, type_code='{self.type_code}', name='{self.name}')>"


class ExpenseRecord(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    """
    费用记录模型
    
    记录具体的费用支出
    """
    
    __tablename__ = "expense_record"
    __table_args__ = (
        CheckConstraint("amount >= 0", name="ck_expense_record_amount"),
        {"comment": "费用记录表"}
    )
    
    # 门店关联
    store_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("store.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="门店ID"
    )
    
    # 费用科目
    expense_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("expense_type.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="费用科目ID"
    )
    
    # 业务日期
    biz_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
        comment="业务日期"
    )
    
    # 金额信息
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="费用金额"
    )
    
    # 费用详情
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="费用说明"
    )
    
    invoice_no: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
        comment="发票号码"
    )
    
    vendor: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="供应商"
    )
    
    # 支付信息
    payment_method: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="支付方式"
    )
    
    payment_account: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="支付账户"
    )
    
    # 审批信息
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="draft",
        index=True,
        comment="状态（draft/submitted/approved/rejected/paid）"
    )
    
    submitted_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="提交日期"
    )
    
    approved_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="审批日期"
    )
    
    approved_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
        comment="审批人ID"
    )
    
    # 创建人
    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="创建人ID"
    )
    
    # 备注
    remark: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    # 关联关系
    store: Mapped["Store"] = relationship("Store")
    expense_type: Mapped["ExpenseType"] = relationship(
        "ExpenseType",
        back_populates="records"
    )
    creator: Mapped["User"] = relationship(
        "User",
        foreign_keys=[created_by]
    )
    approver: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[approved_by]
    )
    
    def __repr__(self) -> str:
        return f"<ExpenseRecord(id={self.id}, store_id={self.store_id}, amount={self.amount})>"