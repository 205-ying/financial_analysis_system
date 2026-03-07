"""
数据库模型包

导入所有模型，确保 Alembic 可以正确发现
"""

# 导入基类（必须先导入）
from app.models.audit_log import AuditLog

# 导入所有模型
from app.models.base import (
    Base,
    IDMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UserTrackingMixin,
)
from app.models.budget import Budget
from app.models.expense import ExpenseRecord, ExpenseType
from app.models.import_job import (
    DataImportJob,
    DataImportJobError,
    ImportJobStatus,
    ImportSourceType,
    ImportTargetType,
)
from app.models.kpi import KpiDailyStore
from app.models.order import OrderHeader, OrderItem
from app.models.store import Product, ProductCategory, Store
from app.models.user import Permission, Role, User, role_permission, user_role
from app.models.user_store import UserStorePermission

# 导出所有模型
__all__ = [
    "Base",
    # Mixins
    "IDMixin",
    "TimestampMixin",
    "SoftDeleteMixin",
    "UserTrackingMixin",
    # User models
    "User",
    "Role",
    "Permission",
    "UserStorePermission",
    "user_role",
    "role_permission",
    # Store models
    "Store",
    "ProductCategory",
    "Product",
    # Order models
    "OrderHeader",
    "OrderItem",
    # Expense models
    "ExpenseType",
    "ExpenseRecord",
    # Budget models
    "Budget",
    # KPI models
    "KpiDailyStore",
    "AuditLog",
    # Import job models
    "DataImportJob",
    "DataImportJobError",
    "ImportSourceType",
    "ImportTargetType",
    "ImportJobStatus",
]
