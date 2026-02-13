"""
Schema 模块

导出所有 Pydantic 模型
"""

from app.schemas.common import Response, success, error, PaginatedResponse
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo
from app.schemas.store import StoreCreate, StoreUpdate, StoreInDB
from app.schemas.order import OrderCreate
from app.schemas.expense_record import ExpenseRecordCreate, ExpenseRecordUpdate
from app.schemas.user_store import UserStoreAssignRequest
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
from app.schemas.product_analysis import (
    ProductSalesRankingItem,
    CategorySalesItem,
    ProductProfitItem,
    ProductABCItem,
    ProductStoreCrossItem,
)
from app.schemas.comparison import (
    ComparisonQuery,
    MetricComparison,
    PeriodComparisonResponse,
    TrendComparisonItem,
    TrendComparisonResponse,
    StoreComparisonItem,
)
from app.schemas.dashboard import (
    SummaryCard,
    TrendDataPoint,
    StoreRankItem,
    ExpenseStructureItem,
    ChannelDistribution,
    DashboardOverview,
)
from app.schemas.budget import (
    BudgetCreate,
    BudgetBatchCreate,
    BudgetItemCreate,
    BudgetUpdate,
    BudgetSchema,
    BudgetAnalysisItem,
    BudgetAnalysisResponse,
)
from app.schemas.cvp import (
    CVPAnalysisResult,
    CostBehaviorUpdate,
    CVPSimulation,
    CVPSimulationResult,
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
    # Order
    "OrderCreate",
    # Expense Record
    "ExpenseRecordCreate",
    "ExpenseRecordUpdate",
    # User Store
    "UserStoreAssignRequest",
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
    # Product Analysis
    "ProductSalesRankingItem",
    "CategorySalesItem",
    "ProductProfitItem",
    "ProductABCItem",
    "ProductStoreCrossItem",
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
    # Comparison
    "ComparisonQuery",
    "MetricComparison",
    "PeriodComparisonResponse",
    "TrendComparisonItem",
    "TrendComparisonResponse",
    "StoreComparisonItem",
    # Dashboard
    "SummaryCard",
    "TrendDataPoint",
    "StoreRankItem",
    "ExpenseStructureItem",
    "ChannelDistribution",
    "DashboardOverview",
    # Budget
    "BudgetCreate",
    "BudgetBatchCreate",
    "BudgetItemCreate",
    "BudgetUpdate",
    "BudgetSchema",
    "BudgetAnalysisItem",
    "BudgetAnalysisResponse",
    # CVP
    "CVPAnalysisResult",
    "CostBehaviorUpdate",
    "CVPSimulation",
    "CVPSimulationResult",
]
