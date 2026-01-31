"""
Schema 模块

导出所有 Pydantic 模型
"""

from app.schemas.common import Response, success, error, PaginatedResponse
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo
from app.schemas.store import StoreCreate, StoreUpdate, StoreInDB
from app.schemas.audit_log import AuditLogListRequest, AuditLogListResponse, AuditLogResponse
from app.schemas.import_job import (
    ImportJobCreate,
    ImportJobDetailOut,
    ImportJobListItem,
    ImportJobErrorListItem,
)
from app.schemas.report import (
    DailySummaryRow,
    MonthlySummaryRow,
    StorePerformanceRow,
    ExpenseBreakdownRow,
)
from app.schemas.kpi import (
    KpiRebuildRequest,
    KpiQueryParams,
    DailyKpiItem,
    KpiSummaryResponse,
    KpiTrendItem,
    KpiTrendResponse,
    ExpenseCategoryItem,
    ExpenseCategoryResponse,
    StoreRankingItem,
    StoreRankingResponse,
    KpiRebuildResponse,
    KpiDailyStoreSchema,
)

__all__ = [
    # Common
    "Response",
    "success",
    "error",
    "PaginatedResponse",
    # Auth
    "LoginRequest",
    "TokenResponse",
    "UserInfo",
    # Store
    "StoreCreate",
    "StoreUpdate",
    "StoreInDB",
    # Audit Log
    "AuditLogListRequest",
    "AuditLogListResponse",
    "AuditLogResponse",
    # Import Job
    "ImportJobCreate",
    "ImportJobDetailOut",
    "ImportJobListItem",
    "ImportJobErrorListItem",
    # Report
    "DailySummaryRow",
    "MonthlySummaryRow",
    "StorePerformanceRow",
    "ExpenseBreakdownRow",
    # KPI
    "KpiRebuildRequest",
    "KpiQueryParams",
    "DailyKpiItem",
    "KpiSummaryResponse",
    "KpiTrendItem",
    "KpiTrendResponse",
    "ExpenseCategoryItem",
    "ExpenseCategoryResponse",
    "StoreRankingItem",
    "StoreRankingResponse",
    "KpiRebuildResponse",
    "KpiDailyStoreSchema",
]
