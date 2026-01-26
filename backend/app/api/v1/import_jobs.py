"""
数据导入任务 API

提供文件上传、任务执行、结果查询和错误报告下载
"""

from typing import List
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, Query, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.models.user import User
from app.models.import_job import ImportTargetType
from app.schemas.common import Response, PaginatedResponse
from app.schemas.import_job import (
    ImportJobCreate,
    ImportJobOut,
    ImportJobDetailOut,
    ImportJobListItem,
    ImportJobErrorListItem,
    ImportJobFilter,
)
from app.services.import_service import ImportService
from app.services.audit_log_service import log_audit
from app.core.exceptions import NotFoundException


router = APIRouter(tags=["数据导入"])


@router.post("", response_model=Response[ImportJobOut])
async def create_import_job(
    file: UploadFile = File(..., description="上传的 Excel 或 CSV 文件"),
    target_type: ImportTargetType = Form(..., description="目标数据类型"),
    job_name: str = Form(None, description="任务名称"),
    store_id: int = Form(None, description="门店ID (订单和费用记录导入必需)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    创建导入任务（上传文件）
    
    - 支持 Excel (.xlsx, .xls) 和 CSV 文件
    - 文件大小限制 50MB
    - 订单和费用记录导入必须指定门店ID
    """
    # 权限检查
    await check_permission(current_user, "import_job:create", db)
    
    # 创建任务
    job = await ImportService.create_job(
        db=db,
        user=current_user,
        upload_file=file,
        target_type=target_type,
        job_name=job_name,
        store_id=store_id,
    )
    
    return Response(
        code=0,
        message="任务创建成功",
        data=ImportJobOut.model_validate(job),
    )


@router.post("/{job_id}/run", response_model=Response[ImportJobOut])
async def run_import_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    执行导入任务
    
    - 解析文件内容
    - 校验数据有效性
    - 批量写入数据库
    - 生成错误报告
    """
    # 权限检查
    await check_permission(current_user, "import_job:run", db)
    
    # 执行任务
    job = await ImportService.run_job(db, job_id, current_user)
    
    return Response(
        code=0,
        message="任务执行完成",
        data=ImportJobOut.model_validate(job),
    )


@router.get("", response_model=PaginatedResponse[List[ImportJobListItem]])
async def list_import_jobs(
    target_type: ImportTargetType = Query(None, description="目标类型筛选"),
    status: str = Query(None, description="状态筛选"),
    created_by_id: int = Query(None, description="创建用户ID筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    分页查询导入任务列表
    
    - 支持按目标类型、状态、创建人筛选
    - 默认按创建时间倒序
    """
    # 权限检查
    await check_permission(current_user, "import_job:view", db)
    
    # 构建过滤条件
    filters = ImportJobFilter(
        target_type=target_type,
        status=status,
        created_by_id=created_by_id,
    )
    
    # 查询任务列表
    jobs, total = await ImportService.list_jobs(db, filters, page, page_size)
    
    return PaginatedResponse(
        code=0,
        message="查询成功",
        data=[ImportJobListItem.model_validate(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{job_id}", response_model=Response[ImportJobDetailOut])
async def get_import_job(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取导入任务详情
    
    - 包含任务配置、创建者信息等
    """
    # 权限检查
    await check_permission(current_user, "import_job:view", db)
    
    # 查询任务
    job = await ImportService.get_job_detail(db, job_id)
    
    return Response(
        code=0,
        message="查询成功",
        data=ImportJobDetailOut.from_orm_with_user(job, include_user=True),
    )


@router.get("/{job_id}/errors", response_model=PaginatedResponse[List[ImportJobErrorListItem]])
async def list_import_job_errors(
    job_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    分页查询导入任务错误记录
    
    - 按行号排序
    - 每页最多200条
    """
    # 权限检查
    await check_permission(current_user, "import_job:view", db)
    
    # 查询错误列表
    errors, total = await ImportService.list_job_errors(db, job_id, page, page_size)
    
    return PaginatedResponse(
        code=0,
        message="查询成功",
        data=[ImportJobErrorListItem.model_validate(err) for err in errors],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{job_id}/error-report")
async def download_error_report(
    job_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    下载错误报告文件
    
    - 返回 CSV 格式的错误明细
    - 包含行号、错误字段、错误信息、原始数据
    """
    # 权限检查
    await check_permission(current_user, "import_job:download", db)
    
    # 获取任务
    job = await ImportService.get_job_detail(db, job_id)
    
    if not job.error_report_path:
        raise NotFoundException("错误报告不存在，可能任务尚未执行或全部成功")
    
    # 检查文件是否存在
    report_path = Path(job.error_report_path)
    if not report_path.exists():
        raise NotFoundException("错误报告文件不存在")
    
    # 记录审计日志
    await log_audit(
        db=db,
        user_id=current_user.id,
        action="download_import_report",
        resource_type="import_job",
        resource_id=job.id,
        detail={
            "job_name": job.job_name,
            "file_name": report_path.name,
        },
    )
    
    # 返回文件
    return FileResponse(
        path=str(report_path),
        filename=f"error_report_{job_id}.csv",
        media_type="text/csv",
    )
