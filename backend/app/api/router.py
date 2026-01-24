"""
API 路由汇总模块
"""

from fastapi import APIRouter
from app.api.v1 import health, auth, stores, orders, kpi, audit
from app.api.v1 import expense_types, expense_records

api_router = APIRouter()

# 注册健康检查路由
api_router.include_router(health.router, tags=["健康检查"])

# 注册认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 注册业务路由
api_router.include_router(stores.router, prefix="/stores", tags=["门店管理"])
api_router.include_router(expense_types.router, prefix="/expense-types", tags=["费用科目管理"])
api_router.include_router(expense_records.router, prefix="/expense-records", tags=["费用记录管理"])
api_router.include_router(orders.router, prefix="/orders", tags=["订单管理"])
api_router.include_router(kpi.router, prefix="/kpi", tags=["KPI 数据"])
api_router.include_router(audit.router, prefix="/audit", tags=["审计日志"])
