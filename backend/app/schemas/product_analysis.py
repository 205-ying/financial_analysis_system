"""
菜品销售分析 Schema

定义菜品分析相关的请求参数和响应模型
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ProductAnalysisQuery(BaseModel):
    """菜品分析查询参数"""
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    store_id: int | None = Field(None, description="门店ID（为空表示全部门店）")
    top_n: int = Field(20, ge=1, le=100, description="返回Top N条记录")
    sort_by: Literal["quantity", "revenue"] = Field("quantity", description="排序字段")


class ProductSalesRankingItem(BaseModel):
    """菜品销量排行项"""
    rank: int = Field(..., description="排名")
    product_name: str = Field(..., description="菜品名称")
    product_category: str | None = Field(None, description="菜品分类")
    total_quantity: float = Field(..., description="总销量")
    total_revenue: float = Field(..., description="总销售额")
    net_revenue: float = Field(..., description="净销售额（扣除折扣）")
    order_count: int = Field(..., description="出现订单数")
    gross_profit: float | None = Field(None, description="毛利润")


class CategorySalesItem(BaseModel):
    """品类销售分布项"""
    category_name: str = Field(..., description="分类名称")
    revenue: float = Field(..., description="销售额")
    quantity: float = Field(..., description="销量")
    percentage: float = Field(..., description="营收占比(%)")


class ProductProfitItem(BaseModel):
    """菜品毛利贡献项"""
    rank: int = Field(..., description="排名")
    product_name: str = Field(..., description="菜品名称")
    product_category: str | None = Field(None, description="菜品分类")
    total_revenue: float = Field(..., description="总销售额")
    total_cost: float = Field(..., description="总成本")
    gross_profit: float = Field(..., description="毛利润")
    profit_margin: float = Field(..., description="毛利率(%)")


class ProductABCItem(BaseModel):
    """菜品ABC分类项"""
    product_name: str = Field(..., description="菜品名称")
    total_revenue: float = Field(..., description="总销售额")
    percentage: float = Field(..., description="营收占比(%)")
    cumulative_percentage: float = Field(..., description="累计占比(%)")
    abc_class: Literal["A", "B", "C"] = Field(..., description="ABC分类")


class ProductStoreCrossItem(BaseModel):
    """菜品-门店交叉分析项"""
    store_name: str = Field(..., description="门店名称")
    product_name: str = Field(..., description="菜品名称")
    quantity: float = Field(..., description="销量")
    revenue: float = Field(..., description="销售额")
