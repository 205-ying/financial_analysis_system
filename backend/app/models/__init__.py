"""
数据库模型包

导入所有模型，确保 Alembic 可以正确发现
"""

# 导入基类（必须先导入）
from app.models.base import Base

# 导入所有模型
from app.models.base import IDMixin, TimestampMixin, SoftDeleteMixin, UserTrackingMixin
from app.models.user import User, Role, Permission, user_role, role_permission
from app.models.user_store import UserStorePermission
from app.models.store import Store, ProductCategory, Product
from app.models.order import OrderHeader, OrderItem
from app.models.expense import ExpenseType, ExpenseRecord
from app.models.kpi import KpiDailyStore
from app.models.audit_log import AuditLog
from app.models.budget import Budget
from app.models.import_job import (
    DataImportJob,
    DataImportJobError,
    ImportSourceType,
    ImportTargetType,
    ImportJobStatus,
)

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