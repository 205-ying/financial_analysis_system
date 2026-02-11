from pydantic import BaseModel, Field

class CVPAnalysisResult(BaseModel):
    """本量利分析结果"""
    # 基础数据
    total_revenue: float = Field(description="总收入")
    variable_cost: float = Field(description="变动成本总额")
    fixed_cost: float = Field(description="固定成本总额")
    
    # 核心指标
    contribution_margin: float = Field(description="边际贡献 = 收入 - 变动成本")
    contribution_margin_rate: float = Field(description="边际贡献率 = 边际贡献 / 收入")
    
    # 盈亏平衡分析
    break_even_point: float = Field(description="盈亏平衡点营收 (BEP)")
    break_even_sales_ratio: float = Field(description="盈亏平衡点销售比率 = BEP / 实际收入")
    
    # 安全性指标
    safety_margin: float = Field(description="安全边际 = 实际收入 - BEP")
    safety_margin_rate: float = Field(description="安全边际率 = 安全边际 / 实际收入")
    
    # 杠杆系数
    operating_leverage: float = Field(description="经营杠杆系数 = 边际贡献 / 利润")
    
    # 实际利润
    operating_profit: float = Field(description="经营利润 = 边际贡献 - 固定成本")

class CostBehaviorUpdate(BaseModel):
    """成本习性更新"""
    expense_type_id: int = Field(description="费用科目ID")
    cost_behavior: str = Field(description="成本习性: fixed 或 variable")

class CVPSimulation(BaseModel):
    """CVP模拟参数"""
    fixed_cost_change_rate: float = Field(0.0, description="固定成本变化率 (%)")
    variable_cost_change_rate: float = Field(0.0, description="变动成本变化率 (%)")
    
class CVPSimulationResult(BaseModel):
    """CVP模拟结果"""
    original_bep: float = Field(description="原盈亏平衡点")
    simulated_bep: float = Field(description="模拟后盈亏平衡点")
    bep_change: float = Field(description="盈亏平衡点变化额")
    bep_change_rate: float = Field(description="盈亏平衡点变化率 (%)")
