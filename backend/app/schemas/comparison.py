"""
同比环比时间对比分析 Schema

定义时间对比分析相关的请求参数和响应模型
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ComparisonQuery(BaseModel):
    """对比分析查询参数"""

    start_date: date = Field(..., description="当期开始日期")
    end_date: date = Field(..., description="当期结束日期")
    compare_type: Literal["yoy", "mom", "custom"] = Field(
        "yoy", description="对比类型: yoy=同比, mom=环比, custom=自定义"
    )
    compare_start_date: date | None = Field(
        None, description="自定义对比期开始日期（compare_type=custom 时必填）"
    )
    compare_end_date: date | None = Field(
        None, description="自定义对比期结束日期（compare_type=custom 时必填）"
    )
    store_id: int | None = Field(None, description="门店ID（为空表示全部门店）")


class MetricComparison(BaseModel):
    """单指标对比结果"""

    metric_name: str = Field(..., description="指标英文名")
    metric_label: str = Field(..., description="指标中文名")
    current_value: float = Field(..., description="当期值")
    previous_value: float = Field(..., description="对比期值")
    difference: float = Field(..., description="差值")
    growth_rate: float | None = Field(None, description="增长率(%)")


class PeriodComparisonResponse(BaseModel):
    """期间对比汇总响应"""

    current_period: str = Field(..., description="当期范围 (如 2024-01-01 ~ 2024-01-31)")
    previous_period: str = Field(..., description="对比期范围")
    metrics: list[MetricComparison] = Field(
        default_factory=list, description="指标对比列表"
    )


class TrendComparisonItem(BaseModel):
    """趋势对比数据项"""

    date_label: str = Field(..., description="日期标签")
    current_value: float = Field(0.0, description="当期值")
    previous_value: float = Field(0.0, description="对比期值")


class TrendComparisonResponse(BaseModel):
    """趋势对比响应"""

    current_period: str = Field(..., description="当期范围")
    previous_period: str = Field(..., description="对比期范围")
    metric_name: str = Field(..., description="指标英文名")
    metric_label: str = Field(..., description="指标中文名")
    data: list[TrendComparisonItem] = Field(
        default_factory=list, description="趋势数据"
    )


class StoreComparisonItem(BaseModel):
    """门店对比数据项"""

    store_id: int = Field(..., description="门店ID")
    store_name: str = Field(..., description="门店名称")
    current_revenue: float = Field(0.0, description="当期营收")
    previous_revenue: float = Field(0.0, description="对比期营收")
    revenue_growth_rate: float | None = Field(None, description="营收增长率(%)")
    current_profit: float = Field(0.0, description="当期利润")
    previous_profit: float = Field(0.0, description="对比期利润")
    profit_growth_rate: float | None = Field(None, description="利润增长率(%)")
    current_order_count: int = Field(0, description="当期订单数")
    previous_order_count: int = Field(0, description="对比期订单数")
    order_growth_rate: float | None = Field(None, description="订单数增长率(%)")
    current_avg_order_value: float = Field(0.0, description="当期客单价")
    previous_avg_order_value: float = Field(0.0, description="对比期客单价")
    avg_order_value_growth_rate: float | None = Field(
        None, description="客单价增长率(%)"
    )
