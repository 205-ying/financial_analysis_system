"""
API 路由汇总模块
"""

from fastapi import APIRouter
from app.api.v1 import health, auth, stores, orders, kpi, audit
from app.api.v1 import expense_types, expense_records, import_jobs, reports, user_stores
from app.api.v1 import roles, permissions
from app.api.v1 import product_analysis
from app.api.v1 import comparison
from app.api.v1 import dashboard

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
api_router.include_router(import_jobs.router, prefix="/import-jobs", tags=["数据导入"])
api_router.include_router(reports.router, prefix="/reports", tags=["报表中心"])
api_router.include_router(user_stores.router, prefix="/user-stores", tags=["用户门店权限"])
api_router.include_router(roles.router, prefix="/roles", tags=["角色管理"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["权限管理"])
api_router.include_router(product_analysis.router, prefix="/product-analysis", tags=["菜品分析"])
api_router.include_router(comparison.router, prefix="/comparison", tags=["同比环比分析"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["管理驾驶舱"])
