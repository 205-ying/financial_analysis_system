"""
数据导入任务 Schema
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict

from app.models.import_job import ImportSourceType, ImportTargetType, ImportJobStatus


# ==================== 请求 Schema ====================

class ImportJobCreate(BaseModel):
    """创建导入任务"""
    job_name: str = Field(..., min_length=1, max_length=200, description="任务名称")
    target_type: ImportTargetType = Field(..., description="目标数据类型")
    store_id: Optional[int] = Field(None, description="门店ID (用于订单和费用记录导入)")
    mapping: Optional[Dict[str, str]] = Field(None, description="字段映射关系 {csv列名: 目标字段名}")


class ImportJobFilter(BaseModel):
    """导入任务查询过滤"""
    target_type: Optional[ImportTargetType] = None
    status: Optional[ImportJobStatus] = None
    created_by_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# ==================== 响应 Schema ====================

class ImportJobErrorOut(BaseModel):
    """导入错误记录输出"""
    id: int
    job_id: int
    row_no: int
    field: Optional[str]
    message: str
    raw_data: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ImportJobOut(BaseModel):
    """导入任务基础输出"""
    id: int
    job_name: str
    source_type: ImportSourceType
    target_type: ImportTargetType
    status: ImportJobStatus
    file_name: str
    total_rows: int
    success_rows: int
    fail_rows: int
    error_report_path: Optional[str]
    created_by_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ImportJobDetailOut(ImportJobOut):
    """导入任务详情输出（含配置和创建者信息）"""
    config: Optional[Dict[str, Any]]
    created_by: Optional[dict] = None  # 简化的用户信息
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm_with_user(cls, job, include_user: bool = True):
        """从 ORM 对象转换，可选包含用户信息"""
        data = {
            "id": job.id,
            "job_name": job.job_name,
            "source_type": job.source_type,
            "target_type": job.target_type,
            "status": job.status,
            "file_name": job.file_name,
            "total_rows": job.total_rows,
            "success_rows": job.success_rows,
            "fail_rows": job.fail_rows,
            "error_report_path": job.error_report_path,
            "created_by_id": job.created_by_id,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "config": job.config,
        }
        
        if include_user and job.created_by:
            data["created_by"] = {
                "id": job.created_by.id,
                "username": job.created_by.username,
                "full_name": job.created_by.full_name,
            }
        
        return cls(**data)


# ==================== 列表响应 ====================

class ImportJobListItem(BaseModel):
    """导入任务列表项（轻量级）"""
    id: int
    job_name: str
    target_type: ImportTargetType
    status: ImportJobStatus
    file_name: str
    total_rows: int
    success_rows: int
    fail_rows: int
    created_by_id: Optional[int]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ImportJobErrorListItem(BaseModel):
    """错误列表项（轻量级）"""
    id: int
    row_no: int
    field: Optional[str]
    message: str
    
    model_config = ConfigDict(from_attributes=True)
