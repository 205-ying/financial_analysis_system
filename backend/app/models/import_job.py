"""
数据导入任务模型

记录 Excel/CSV 数据导入任务的状态、结果和错误信息
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from enum import Enum

from app.models.base import Base, IDMixin, TimestampMixin


class ImportSourceType(str, Enum):
    """导入源类型"""
    EXCEL = "excel"
    CSV = "csv"


class ImportTargetType(str, Enum):
    """导入目标类型"""
    ORDERS = "orders"
    EXPENSE_RECORDS = "expense_records"
    STORES = "stores"
    EXPENSE_TYPES = "expense_types"


class ImportJobStatus(str, Enum):
    """导入任务状态"""
    PENDING = "pending"           # 待处理
    RUNNING = "running"           # 运行中
    SUCCESS = "success"           # 全部成功
    PARTIAL_FAIL = "partial_fail" # 部分失败
    FAIL = "fail"                 # 全部失败


class DataImportJob(Base, IDMixin, TimestampMixin):
    """数据导入任务表"""
    
    __tablename__ = "data_import_jobs"
    
    job_name = Column(String(200), nullable=False, comment="任务名称")
    source_type = Column(
        SQLEnum(ImportSourceType, name="import_source_type", create_type=False),
        nullable=False,
        comment="源文件类型 (excel/csv)"
    )
    target_type = Column(
        SQLEnum(ImportTargetType, name="import_target_type", create_type=False),
        nullable=False,
        comment="目标数据类型 (orders/expense_records/stores/expense_types)"
    )
    status = Column(
        SQLEnum(ImportJobStatus, name="import_job_status", create_type=False),
        nullable=False,
        default=ImportJobStatus.PENDING,
        comment="任务状态"
    )
    
    # 文件信息
    file_name = Column(String(500), nullable=False, comment="原始文件名")
    file_path = Column(String(1000), nullable=False, comment="文件存储路径")
    
    # 导入结果统计
    total_rows = Column(Integer, nullable=False, default=0, comment="总行数")
    success_rows = Column(Integer, nullable=False, default=0, comment="成功行数")
    fail_rows = Column(Integer, nullable=False, default=0, comment="失败行数")
    
    # 错误报告
    error_report_path = Column(String(1000), nullable=True, comment="错误报告文件路径")
    
    # 额外配置（存储字段映射、门店ID等）
    config = Column(JSONB, nullable=True, comment="任务配置 (映射关系、门店ID等)")
    
    # 创建用户
    created_by_id = Column(Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, comment="创建用户ID")
    
    # 关系
    created_by = relationship("User", foreign_keys=[created_by_id])
    errors = relationship("DataImportJobError", back_populates="job", cascade="all, delete-orphan")
    
    # 索引
    __table_args__ = (
        Index("idx_import_job_status", "status"),
        Index("idx_import_job_target_type", "target_type"),
        Index("idx_import_job_created_at", "created_at"),
        Index("idx_import_job_created_by", "created_by_id"),
    )
    
    def __repr__(self):
        return f"<DataImportJob(id={self.id}, job_name='{self.job_name}', status='{self.status}')>"


class DataImportJobError(Base, IDMixin, TimestampMixin):
    """数据导入错误记录表"""
    
    __tablename__ = "data_import_job_errors"
    
    job_id = Column(Integer, ForeignKey("data_import_jobs.id", ondelete="CASCADE"), nullable=False, comment="任务ID")
    row_no = Column(Integer, nullable=False, comment="错误行号 (从1开始)")
    field = Column(String(100), nullable=True, comment="错误字段")
    message = Column(Text, nullable=False, comment="错误信息")
    raw_data = Column(JSONB, nullable=True, comment="原始行数据")
    
    # 关系
    job = relationship("DataImportJob", back_populates="errors")
    
    # 索引
    __table_args__ = (
        Index("idx_import_error_job_id", "job_id"),
        Index("idx_import_error_row_no", "job_id", "row_no"),
    )
    
    def __repr__(self):
        return f"<DataImportJobError(id={self.id}, job_id={self.job_id}, row_no={self.row_no})>"
