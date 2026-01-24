"""
门店和产品模型

包含门店、产品分类和产品信息
"""

from __future__ import annotations

from decimal import Decimal
from typing import List

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin, SoftDeleteMixin


class Store(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    """
    门店模型
    
    存储餐饮门店基本信息
    """
    
    __tablename__ = "store"
    __table_args__ = (
        UniqueConstraint("code", name="uq_store_code"),
        {"comment": "门店表"}
    )
    
    # 基本信息
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="门店编码"
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="门店名称"
    )
    
    # 联系信息
    address: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
        comment="门店地址"
    )
    
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="联系电话"
    )
    
    contact_person: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="联系人"
    )
    
    # 营业信息
    business_hours: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="营业时间"
    )
    
    area_sqm: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="营业面积（平方米）"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否营业"
    )
    
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序顺序"
    )
    
    remark: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="备注"
    )
    
    def __repr__(self) -> str:
        return f"<Store(id={self.id}, code='{self.code}', name='{self.name}')>"


class ProductCategory(Base, IDMixin, TimestampMixin):
    """
    产品分类模型
    
    支持树形结构的产品分类
    """
    
    __tablename__ = "product_category"
    __table_args__ = (
        UniqueConstraint("code", name="uq_product_category_code"),
        {"comment": "产品分类表"}
    )
    
    # 基本信息
    code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="分类编码"
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="分类名称"
    )
    
    # 树形结构
    parent_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("product_category.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="父分类ID"
    )
    
    level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="层级"
    )
    
    # 其他信息
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="分类描述"
    )
    
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
    
    # 关联关系
    parent: Mapped["ProductCategory | None"] = relationship(
        "ProductCategory",
        remote_side="ProductCategory.id",
        back_populates="children"
    )
    
    children: Mapped[List["ProductCategory"]] = relationship(
        "ProductCategory",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="category"
    )
    
    def __repr__(self) -> str:
        return f"<ProductCategory(id={self.id}, code='{self.code}', name='{self.name}')>"


class Product(Base, IDMixin, TimestampMixin, SoftDeleteMixin):
    """
    产品模型
    
    存储菜品、商品信息
    """
    
    __tablename__ = "product"
    __table_args__ = (
        UniqueConstraint("sku_code", name="uq_product_sku_code"),
        {"comment": "产品表"}
    )
    
    # 基本信息
    sku_code: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="SKU编码"
    )
    
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="产品名称"
    )
    
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("product_category.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="分类ID"
    )
    
    # 价格信息
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="单价"
    )
    
    cost_price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="成本价"
    )
    
    # 库存信息
    unit: Mapped[str] = mapped_column(
        String(20),
        default="份",
        nullable=False,
        comment="单位"
    )
    
    # 产品属性
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="产品描述"
    )
    
    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="产品图片URL"
    )
    
    # 状态信息
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="是否在售"
    )
    
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否推荐"
    )
    
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序顺序"
    )
    
    # 关联关系
    category: Mapped["ProductCategory"] = relationship(
        "ProductCategory",
        back_populates="products"
    )
    
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, sku_code='{self.sku_code}', name='{self.name}')>"