"""
KPI 相关 Schema 定义

包含 KPI 数据的请求和响应模型
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ==================== 请求模型 ====================

class KpiRebuildRequest(BaseModel):
    """KPI 重建请求"""
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    store_id: Optional[int] = Field(None, description="门店ID（可选，不填则重建所有门店）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "store_id": 1
            }
        }


class KpiQueryParams(BaseModel):
    """KPI 查询参数"""
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    store_id: Optional[int] = Field(None, description="门店ID")
    granularity: Optional[str] = Field("day", description="粒度：day/week/month")
    top_n: Optional[int] = Field(10, description="Top N 数量")


# ==================== 响应模型 ====================

class DailyKpiItem(BaseModel):
    """日度 KPI 数据项"""
    id: int = Field(..., description="记录ID")
    store_id: int = Field(..., description="门店ID")
    store_name: Optional[str] = Field(None, description="门店名称")
    business_date: str = Field(..., description="业务日期")
    
    # 营收指标
    sales_amount: float = Field(0, description="营业收入")
    net_revenue: Optional[float] = Field(0, description="净收入")
    refund_amount: Optional[float] = Field(0, description="退款金额")
    discount_amount: Optional[float] = Field(0, description="优惠金额")
    
    # 订单指标
    order_count: int = Field(0, description="订单数")
    customer_count: int = Field(0, description="客户数")
    avg_order_value: float = Field(0, description="客单价")
    
    # 渠道分布
    dine_in_revenue: Optional[float] = Field(0, description="堂食收入")
    takeout_revenue: Optional[float] = Field(0, description="外带收入")
    delivery_revenue: Optional[float] = Field(0, description="外卖收入")
    
    class Config:
        from_attributes = True


class KpiSummaryResponse(BaseModel):
    """KPI 汇总响应"""
    total_revenue: float = Field(0, description="总营收")
    total_cost: float = Field(0, description="总成本")
    total_profit: float = Field(0, description="总利润")
    profit_rate: float = Field(0, description="利润率")
    order_count: int = Field(0, description="订单数")
    expense_count: int = Field(0, description="费用记录数")
    store_count: int = Field(0, description="门店数量")
    date_range: Dict[str, str] = Field(..., description="日期范围")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_revenue": 100000.00,
                "total_cost": 70000.00,
                "total_profit": 30000.00,
                "profit_rate": 0.30,
                "order_count": 1500,
                "expense_count": 200,
                "store_count": 5,
                "date_range": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-01-31"
                }
            }
        }


class KpiTrendItem(BaseModel):
    """KPI 趋势数据项"""
    date: str = Field(..., description="日期")
    revenue: float = Field(0, description="营收")
    cost: float = Field(0, description="成本")
    profit: float = Field(0, description="利润")
    profit_rate: Optional[float] = Field(0, description="利润率")
    order_count: int = Field(0, description="订单数")


class KpiTrendSummary(BaseModel):
    """KPI 趋势汇总"""
    total_revenue: float = Field(0, description="总营收")
    total_cost: float = Field(0, description="总成本")
    total_profit: float = Field(0, description="总利润")
    total_orders: int = Field(0, description="总订单数")
    data_points: int = Field(0, description="数据点数量")


class KpiTrendResponse(BaseModel):
    """KPI 趋势响应"""
    items: List[KpiTrendItem] = Field(default_factory=list, description="趋势数据列表")
    summary: KpiTrendSummary = Field(..., description="汇总数据")
    granularity: str = Field("day", description="时间粒度")
    date_range: Dict[str, str] = Field(..., description="日期范围")


class ExpenseCategoryItem(BaseModel):
    """费用分类统计项"""
    category_id: Optional[int] = Field(None, description="费用类型ID")
    category_code: Optional[str] = Field(None, description="费用类型编码")
    category_name: str = Field(..., description="费用类型名称")
    total_amount: float = Field(0, description="总金额")
    amount: Optional[float] = Field(0, description="金额（兼容字段）")
    percentage: float = Field(0, description="占比（百分比）")
    record_count: Optional[int] = Field(0, description="记录数")


class ExpenseCategoryResponse(BaseModel):
    """费用分类统计响应"""
    categories: List[ExpenseCategoryItem] = Field(default_factory=list, description="分类列表")
    total_amount: float = Field(0, description="费用总额")
    date_range: Dict[str, str] = Field(..., description="日期范围")


class StoreRankingItem(BaseModel):
    """门店排名数据项"""
    store_id: int = Field(..., description="门店ID")
    store_name: str = Field(..., description="门店名称")
    revenue: float = Field(0, description="营收")
    cost: float = Field(0, description="成本")
    profit: float = Field(0, description="利润")
    profit_margin: float = Field(0, description="利润率（百分比）")
    order_count: int = Field(0, description="订单数")
    rank: int = Field(0, description="排名")
    
    # 兼容字段（与前端类型匹配）
    total_revenue: Optional[float] = Field(None, description="总营收（兼容字段）")
    total_cost: Optional[float] = Field(None, description="总成本（兼容字段）")
    total_profit: Optional[float] = Field(None, description="总利润（兼容字段）")
    profit_rate: Optional[float] = Field(None, description="利润率（兼容字段）")


class StoreRankingResponse(BaseModel):
    """门店排名响应"""
    stores: List[StoreRankingItem] = Field(default_factory=list, description="门店列表")
    total_stores: int = Field(0, description="门店总数")
    sort_by: str = Field("profit", description="排序字段")
    top_n: Any = Field(10, description="Top N 数量")
    date_range: Dict[str, str] = Field(..., description="日期范围")


class KpiRebuildResponse(BaseModel):
    """KPI 重建响应"""
    message: str = Field(..., description="操作结果消息")
    affected_dates: int = Field(0, description="影响的日期数")
    affected_stores: int = Field(0, description="影响的门店数")
    total_records: int = Field(0, description="处理的记录总数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "KPI数据重建完成",
                "affected_dates": 31,
                "affected_stores": 5,
                "total_records": 155
            }
        }


# ==================== 完整 KPI 数据模型（与数据库模型对应） ====================

class KpiDailyStoreSchema(BaseModel):
    """门店日度 KPI 完整 Schema（与数据库模型 KpiDailyStore 对应）"""
    id: int
    biz_date: date = Field(..., description="业务日期")
    store_id: int = Field(..., description="门店ID")
    
    # 营收指标
    revenue: Decimal = Field(default=Decimal("0.00"), description="营业收入")
    refund_amount: Decimal = Field(default=Decimal("0.00"), description="退款金额")
    discount_amount: Decimal = Field(default=Decimal("0.00"), description="优惠金额")
    net_revenue: Decimal = Field(default=Decimal("0.00"), description="净收入")
    
    # 成本指标
    cost_total: Decimal = Field(default=Decimal("0.00"), description="总成本")
    cost_material: Decimal = Field(default=Decimal("0.00"), description="原材料成本")
    cost_labor: Decimal = Field(default=Decimal("0.00"), description="人工成本")
    cost_rent: Decimal = Field(default=Decimal("0.00"), description="租金成本")
    cost_utilities: Decimal = Field(default=Decimal("0.00"), description="水电煤成本")
    cost_marketing: Decimal = Field(default=Decimal("0.00"), description="营销成本")
    cost_other: Decimal = Field(default=Decimal("0.00"), description="其他成本")
    
    # 利润指标
    gross_profit: Decimal = Field(default=Decimal("0.00"), description="毛利润")
    operating_profit: Decimal = Field(default=Decimal("0.00"), description="营业利润")
    profit_rate: Decimal = Field(default=Decimal("0.0000"), description="利润率")
    
    # 订单指标
    order_count: int = Field(default=0, description="订单数")
    customer_count: int = Field(default=0, description="客户数")
    avg_order_value: Decimal = Field(default=Decimal("0.00"), description="客单价")
    
    # 渠道分布
    dine_in_revenue: Decimal = Field(default=Decimal("0.00"), description="堂食收入")
    takeout_revenue: Decimal = Field(default=Decimal("0.00"), description="外带收入")
    delivery_revenue: Decimal = Field(default=Decimal("0.00"), description="外卖收入")
    online_revenue: Decimal = Field(default=Decimal("0.00"), description="线上收入")
    
    # 备注
    remark: Optional[str] = Field(None, description="备注")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "biz_date": "2024-01-15",
                "store_id": 1,
                "revenue": "15000.00",
                "net_revenue": "14500.00",
                "cost_total": "10000.00",
                "gross_profit": "4500.00",
                "profit_rate": "0.3000",
                "order_count": 120,
                "customer_count": 100,
                "avg_order_value": "125.00"
            }
        }
