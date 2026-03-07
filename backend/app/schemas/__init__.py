"""
Schema 模块

导出所有 Pydantic 模型
"""

from app.schemas.audit_log import (
    AuditLogListRequest,
    AuditLogListResponse,
    AuditLogResponse,
)
from app.schemas.auth import LoginRequest, TokenResponse, UserInfo
from app.schemas.budget import (
    BudgetAnalysisItem,
    BudgetAnalysisResponse,
    BudgetBatchCreate,
    BudgetCreate,
    BudgetItemCreate,
    BudgetSchema,
    BudgetUpdate,
)
from app.schemas.common import PaginatedResponse, Response, error, success
from app.schemas.comparison import (
    ComparisonQuery,
    MetricComparison,
    PeriodComparisonResponse,
    StoreComparisonItem,
    TrendComparisonItem,
    TrendComparisonResponse,
)
from app.schemas.cvp import (
    CostBehaviorUpdate,
    CVPAnalysisResult,
    CVPSimulation,
    CVPSimulationResult,
)
from app.schemas.dashboard import (
    ChannelDistribution,
    DashboardOverview,
    ExpenseStructureItem,
    StoreRankItem,
    SummaryCard,
    TrendDataPoint,
)
from app.schemas.expense_record import ExpenseRecordCreate, ExpenseRecordUpdate
from app.schemas.import_job import (
    ImportJobCreate,
    ImportJobDetailOut,
    ImportJobErrorListItem,
    ImportJobListItem,
)
from app.schemas.kpi import (
    DailyKpiItem,
    ExpenseCategoryItem,
    ExpenseCategoryResponse,
    KpiDailyStoreSchema,
    KpiQueryParams,
    KpiRebuildRequest,
    KpiRebuildResponse,
    KpiSummaryResponse,
    KpiTrendItem,
    KpiTrendResponse,
    StoreRankingItem,
    StoreRankingResponse,
)
from app.schemas.order import OrderCreate
from app.schemas.product_analysis import (
    CategorySalesItem,
    ProductABCItem,
    ProductProfitItem,
    ProductSalesRankingItem,
    ProductStoreCrossItem,
)
from app.schemas.report import (
    DailySummaryRow,
    ExpenseBreakdownRow,
    MonthlySummaryRow,
    StorePerformanceRow,
)
from app.schemas.store import StoreCreate, StoreInDB, StoreUpdate
from app.schemas.user_store import UserStoreAssignRequest

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
