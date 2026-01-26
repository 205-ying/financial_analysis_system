"""
报表模块 Schema 定义
"""
from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


# ==================== 查询参数 ====================

class ReportQuery(BaseModel):
    """报表查询参数"""
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    store_id: Optional[int] = Field(None, description="门店ID（为空表示全部门店）")
    top_n: Optional[int] = Field(None, ge=1, le=100, description="TOP N排名（1-100）")
    group_by: Optional[str] = Field(None, description="分组字段（day/week/month/store）")


# ==================== 响应模型 ====================

class DailySummaryRow(BaseModel):
    """日汇总行"""
    biz_date: date = Field(..., description="业务日期")
    store_id: Optional[int] = Field(None, description="门店ID")
    store_name: Optional[str] = Field(None, description="门店名称")
    
    # 营收指标
    revenue: Decimal = Field(default=Decimal("0.00"), description="营业收入")
    net_revenue: Decimal = Field(default=Decimal("0.00"), description="净收入")
    discount_amount: Decimal = Field(default=Decimal("0.00"), description="优惠金额")
    refund_amount: Decimal = Field(default=Decimal("0.00"), description="退款金额")
    
    # 成本指标
    cost_total: Decimal = Field(default=Decimal("0.00"), description="总成本")
    cost_material: Decimal = Field(default=Decimal("0.00"), description="原材料成本")
    cost_labor: Decimal = Field(default=Decimal("0.00"), description="人工成本")
    
    # 费用指标
    expense_total: Decimal = Field(default=Decimal("0.00"), description="总费用")
    
    # 订单指标
    order_count: int = Field(default=0, description="订单数")
    
    # 利润指标
    gross_profit: Decimal = Field(default=Decimal("0.00"), description="毛利润")
    operating_profit: Decimal = Field(default=Decimal("0.00"), description="营业利润")
    gross_profit_rate: Optional[Decimal] = Field(None, description="毛利率（%）")
    operating_profit_rate: Optional[Decimal] = Field(None, description="营业利润率（%）")
    
    class Config:
        from_attributes = True


class MonthlySummaryRow(BaseModel):
    """月汇总行"""
    year: int = Field(..., description="年份")
    month: int = Field(..., description="月份")
    store_id: Optional[int] = Field(None, description="门店ID")
    store_name: Optional[str] = Field(None, description="门店名称")
    
    # 营收指标
    revenue: Decimal = Field(default=Decimal("0.00"), description="营业收入")
    net_revenue: Decimal = Field(default=Decimal("0.00"), description="净收入")
    discount_amount: Decimal = Field(default=Decimal("0.00"), description="优惠金额")
    refund_amount: Decimal = Field(default=Decimal("0.00"), description="退款金额")
    
    # 成本指标
    cost_total: Decimal = Field(default=Decimal("0.00"), description="总成本")
    
    # 费用指标
    expense_total: Decimal = Field(default=Decimal("0.00"), description="总费用")
    
    # 订单指标
    order_count: int = Field(default=0, description="订单数")
    
    # 利润指标
    gross_profit: Decimal = Field(default=Decimal("0.00"), description="毛利润")
    operating_profit: Decimal = Field(default=Decimal("0.00"), description="营业利润")
    gross_profit_rate: Optional[Decimal] = Field(None, description="毛利率（%）")
    operating_profit_rate: Optional[Decimal] = Field(None, description="营业利润率（%）")
    
    # 日均指标
    avg_daily_revenue: Decimal = Field(default=Decimal("0.00"), description="日均收入")
    avg_daily_order_count: Decimal = Field(default=Decimal("0.00"), description="日均订单数")
    
    class Config:
        from_attributes = True


class StorePerformanceRow(BaseModel):
    """门店绩效行"""
    store_id: int = Field(..., description="门店ID")
    store_name: str = Field(..., description="门店名称")
    
    # 营收指标
    revenue: Decimal = Field(default=Decimal("0.00"), description="营业收入")
    net_revenue: Decimal = Field(default=Decimal("0.00"), description="净收入")
    
    # 订单指标
    order_count: int = Field(default=0, description="订单数")
    avg_order_amount: Decimal = Field(default=Decimal("0.00"), description="客单价")
    
    # 利润指标
    gross_profit: Decimal = Field(default=Decimal("0.00"), description="毛利润")
    operating_profit: Decimal = Field(default=Decimal("0.00"), description="营业利润")
    gross_profit_rate: Optional[Decimal] = Field(None, description="毛利率（%）")
    operating_profit_rate: Optional[Decimal] = Field(None, description="营业利润率（%）")
    
    # 排名
    revenue_rank: Optional[int] = Field(None, description="营收排名")
    profit_rank: Optional[int] = Field(None, description="利润排名")
    
    class Config:
        from_attributes = True


class ExpenseBreakdownRow(BaseModel):
    """费用明细行"""
    expense_type_id: int = Field(..., description="费用科目ID")
    expense_type_code: str = Field(..., description="费用科目编码")
    expense_type_name: str = Field(..., description="费用科目名称")
    category: str = Field(..., description="费用类别")
    
    # 门店信息（可选）
    store_id: Optional[int] = Field(None, description="门店ID")
    store_name: Optional[str] = Field(None, description="门店名称")
    
    # 费用统计
    total_amount: Decimal = Field(default=Decimal("0.00"), description="费用总额")
    record_count: int = Field(default=0, description="记录笔数")
    avg_amount: Decimal = Field(default=Decimal("0.00"), description="平均单笔金额")
    
    # 占比
    percentage: Optional[Decimal] = Field(None, description="占总费用比例（%）")
    
    class Config:
        from_attributes = True
