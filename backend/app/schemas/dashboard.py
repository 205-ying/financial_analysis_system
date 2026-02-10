"""
Dashboard 仪表盘 Schema

定义管理驾驶舱相关的请求参数和响应模型
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class SummaryCard(BaseModel):
    """核心指标卡片"""

    label: str = Field(..., description="指标名称")
    value: float = Field(0.0, description="当前值")
    unit: str = Field("元", description="单位: 元/笔/%/家")
    yoy_growth: float | None = Field(None, description="同比增长率(%)")
    mom_growth: float | None = Field(None, description="环比增长率(%)")


class TrendDataPoint(BaseModel):
    """趋势数据点"""

    date: str = Field(..., description="日期 (YYYY-MM-DD)")
    revenue: float = Field(0.0, description="营收")
    cost: float = Field(0.0, description="成本")
    profit: float = Field(0.0, description="利润")


class StoreRankItem(BaseModel):
    """门店排名项"""

    store_name: str = Field(..., description="门店名称")
    revenue: float = Field(0.0, description="营收")
    profit: float = Field(0.0, description="利润")


class ExpenseStructureItem(BaseModel):
    """费用结构项"""

    name: str = Field(..., description="费用类型名称")
    value: float = Field(0.0, description="费用金额")


class ChannelDistribution(BaseModel):
    """渠道收入分布"""

    dine_in: float = Field(0.0, description="堂食收入")
    takeout: float = Field(0.0, description="外带收入")
    delivery: float = Field(0.0, description="外卖收入")
    online: float = Field(0.0, description="线上收入")


class DashboardOverview(BaseModel):
    """仪表盘全量数据"""

    summary_cards: list[SummaryCard] = Field(
        default_factory=list, description="核心指标卡片"
    )
    revenue_trend: list[TrendDataPoint] = Field(
        default_factory=list, description="营收趋势"
    )
    store_ranking: list[StoreRankItem] = Field(
        default_factory=list, description="门店排名"
    )
    expense_structure: list[ExpenseStructureItem] = Field(
        default_factory=list, description="费用结构"
    )
    channel_distribution: ChannelDistribution = Field(
        default_factory=lambda: ChannelDistribution(), description="渠道分布"
    )
    profit_rate: float = Field(0.0, description="当前利润率(%)")
    profit_rate_target: float = Field(15.0, description="目标利润率(%)")
