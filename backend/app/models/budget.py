from sqlalchemy import Column, Integer, ForeignKey, DECIMAL, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModelWithUserTracking

class Budget(BaseModelWithUserTracking):
    """
    预算模型
    用于存储每家门店、每个月、每个费用科目的预算金额
    """
    __tablename__ = "budgets"

    store_id = Column(Integer, ForeignKey("store.id"), nullable=False, comment="门店ID")
    expense_type_id = Column(Integer, ForeignKey("expense_type.id"), nullable=False, comment="费用科目ID")
    year = Column(Integer, nullable=False, comment="年份")
    month = Column(Integer, nullable=False, comment="月份")
    amount = Column(DECIMAL(10, 2), nullable=False, comment="预算金额")

    # 关联关系
    store = relationship("Store", backref="budgets")
    expense_type = relationship("ExpenseType", backref="budgets")

    # 唯一约束：确保每个门店每月的每个科目只有一个预算记录（避免重复）
    __table_args__ = (
        UniqueConstraint('store_id', 'expense_type_id', 'year', 'month', name='uq_budget_store_expense_date'),
    )
