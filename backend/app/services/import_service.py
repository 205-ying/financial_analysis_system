"""
数据导入服务

处理 Excel/CSV 文件导入，包括文件解析、数据校验、批量写入和错误处理
"""

import os
import csv
import shutil
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

import pandas as pd
from fastapi import UploadFile
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ValidationException,
    BusinessException,
    NotFoundException,
)
from app.models.import_job import (
    DataImportJob,
    DataImportJobError,
    ImportSourceType,
    ImportTargetType,
    ImportJobStatus,
)
from app.models.order import OrderHeader, OrderItem
from app.models.expense import ExpenseType, ExpenseRecord
from app.models.store import Store
from app.models.user import User
from app.schemas.import_job import ImportJobFilter


# 上传文件配置
UPLOAD_BASE_DIR = Path("backend/uploads/imports")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".csv"}
MAX_ROWS_PER_JOB = 10000  # 单次导入最大行数


class ImportService:
    """数据导入服务"""
    
    @staticmethod
    async def create_job(
        db: AsyncSession,
        user: User,
        upload_file: UploadFile,
        target_type: ImportTargetType,
        job_name: Optional[str] = None,
        mapping: Optional[Dict[str, str]] = None,
        store_id: Optional[int] = None,
    ) -> DataImportJob:
        """
        创建导入任务
        
        Args:
            db: 数据库会话
            user: 当前用户
            upload_file: 上传的文件
            target_type: 目标数据类型
            job_name: 任务名称
            mapping: 字段映射
            store_id: 门店ID (订单和费用记录必需)
        
        Returns:
            创建的任务对象
        """
        # 1. 文件校验
        if not upload_file.filename:
            raise ValidationException("文件名不能为空")
        
        file_ext = Path(upload_file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(f"不支持的文件格式，仅支持: {', '.join(ALLOWED_EXTENSIONS)}")
        
        # 检查文件大小
        content = await upload_file.read()
        await upload_file.seek(0)  # 重置文件指针
        
        if len(content) > MAX_FILE_SIZE:
            raise ValidationException(f"文件大小超过限制 ({MAX_FILE_SIZE // 1024 // 1024}MB)")
        
        # 2. 业务校验
        if target_type in [ImportTargetType.ORDERS, ImportTargetType.EXPENSE_RECORDS]:
            if not store_id:
                raise ValidationException(f"导入 {target_type.value} 必须指定门店ID")
            
            # 验证门店存在
            store = await db.get(Store, store_id)
            if not store:
                raise NotFoundException(f"门店 {store_id} 不存在")
        
        # 3. 推断源文件类型
        source_type = ImportSourceType.EXCEL if file_ext in [".xlsx", ".xls"] else ImportSourceType.CSV
        
        # 4. 创建任务记录
        job = DataImportJob(
            job_name=job_name or f"{target_type.value}_导入_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_type=source_type,
            target_type=target_type,
            status=ImportJobStatus.PENDING,
            file_name=upload_file.filename,
            file_path="",  # 稍后更新
            total_rows=0,
            success_rows=0,
            fail_rows=0,
            config={
                "mapping": mapping or {},
                "store_id": store_id,
            },
            created_by_id=user.id,
        )
        
        db.add(job)
        await db.flush()  # 获取 job.id
        
        # 5. 保存文件
        job_dir = UPLOAD_BASE_DIR / str(job.id)
        job_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = job_dir / upload_file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        job.file_path = str(file_path)
        await db.commit()
        await db.refresh(job)
        
        return job
    
    @staticmethod
    async def run_job(db: AsyncSession, job_id: int, user: User) -> DataImportJob:
        """
        执行导入任务
        
        Args:
            db: 数据库会话
            job_id: 任务ID
            user: 当前用户
        
        Returns:
            更新后的任务对象
        """
        # 1. 获取任务
        job = await db.get(DataImportJob, job_id)
        if not job:
            raise NotFoundException(f"导入任务 {job_id} 不存在")
        
        # 2. 状态校验（防止重复执行）
        if job.status == ImportJobStatus.RUNNING:
            raise BusinessException("任务正在运行中，请勿重复执行")
        
        if job.status in [ImportJobStatus.SUCCESS, ImportJobStatus.PARTIAL_FAIL]:
            raise BusinessException("任务已执行完成，不可重复执行")
        
        # 3. 更新状态为运行中
        job.status = ImportJobStatus.RUNNING
        await db.commit()
        
        try:
            # 4. 解析文件
            rows = await ImportService._parse_file(job)
            job.total_rows = len(rows)
            
            # 检查行数限制
            if len(rows) > MAX_ROWS_PER_JOB:
                raise ValidationException(
                    f"数据行数超过限制 (最大 {MAX_ROWS_PER_JOB} 行，当前 {len(rows)} 行)，请分批导入"
                )
            
            # 5. 根据目标类型执行导入
            if job.target_type == ImportTargetType.ORDERS:
                await ImportService._import_orders(db, job, rows)
            elif job.target_type == ImportTargetType.EXPENSE_RECORDS:
                await ImportService._import_expense_records(db, job, rows)
            elif job.target_type == ImportTargetType.STORES:
                await ImportService._import_stores(db, job, rows)
            elif job.target_type == ImportTargetType.EXPENSE_TYPES:
                await ImportService._import_expense_types(db, job, rows)
            else:
                raise BusinessException(f"不支持的导入类型: {job.target_type}")
            
            # 6. 更新任务状态
            if job.fail_rows == 0:
                job.status = ImportJobStatus.SUCCESS
            elif job.success_rows > 0:
                job.status = ImportJobStatus.PARTIAL_FAIL
            else:
                job.status = ImportJobStatus.FAIL
            
            # 7. 生成错误报告
            if job.fail_rows > 0:
                await ImportService.build_error_report(db, job_id)
            
            await db.commit()
            await db.refresh(job)
            
            return job
        
        except Exception as e:
            # 任务失败
            job.status = ImportJobStatus.FAIL
            await db.commit()
            raise
    
    @staticmethod
    async def _parse_file(job: DataImportJob) -> List[Dict[str, Any]]:
        """解析文件内容"""
        file_path = Path(job.file_path)
        
        if not file_path.exists():
            raise BusinessException(f"文件不存在: {job.file_path}")
        
        try:
            if job.source_type == ImportSourceType.CSV:
                # CSV 文件
                df = pd.read_csv(file_path, encoding="utf-8")
            else:
                # Excel 文件
                df = pd.read_excel(file_path, engine="openpyxl")
            
            # 转换为字典列表
            df = df.fillna("")  # 填充空值
            rows = df.to_dict(orient="records")
            
            return rows
        
        except Exception as e:
            raise ValidationException(f"文件解析失败: {str(e)}")
    
    @staticmethod
    async def _import_orders(db: AsyncSession, job: DataImportJob, rows: List[Dict[str, Any]]):
        """导入订单数据"""
        store_id = job.config.get("store_id")
        mapping = job.config.get("mapping", {})
        
        # 字段映射（支持自定义）
        def get_field(row: dict, field: str, default=None):
            mapped_field = mapping.get(field, field)
            return row.get(mapped_field, default)
        
        # 批量查询已存在的订单号
        order_nos = [get_field(row, "order_no", "") for row in rows if get_field(row, "order_no")]
        existing_orders = await db.execute(
            select(OrderHeader.order_no).where(OrderHeader.order_no.in_(order_nos))
        )
        existing_order_nos = set(result[0] for result in existing_orders.all())
        
        success_count = 0
        fail_count = 0
        
        for idx, row in enumerate(rows, start=1):
            try:
                # 1. 提取字段
                order_no = get_field(row, "order_no", "").strip()
                biz_date_str = get_field(row, "biz_date", "").strip()
                gross_amount_str = get_field(row, "gross_amount", "")
                discount_amount_str = get_field(row, "discount_amount", "0")
                net_amount_str = get_field(row, "net_amount", "")
                customer_count_str = get_field(row, "customer_count", "1")
                
                # 2. 必填字段校验
                if not order_no:
                    raise ValueError("订单号不能为空")
                
                if not biz_date_str:
                    raise ValueError("业务日期不能为空")
                
                if not net_amount_str and not gross_amount_str:
                    raise ValueError("交易金额不能为空")
                
                # 3. 幂等性检查：订单号唯一
                if order_no in existing_order_nos:
                    raise ValueError(f"订单号 {order_no} 已存在，不可重复导入")
                
                # 4. 数据转换
                try:
                    biz_date = datetime.strptime(str(biz_date_str), "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"业务日期格式错误，应为 YYYY-MM-DD: {biz_date_str}")
                
                try:
                    gross_amount = Decimal(str(gross_amount_str)) if gross_amount_str else Decimal("0")
                    discount_amount = Decimal(str(discount_amount_str)) if discount_amount_str else Decimal("0")
                    net_amount = Decimal(str(net_amount_str)) if net_amount_str else gross_amount - discount_amount
                except (InvalidOperation, ValueError) as e:
                    raise ValueError(f"金额格式错误: {e}")
                
                # 金额校验
                if gross_amount < 0 or discount_amount < 0 or net_amount < 0:
                    raise ValueError("金额不能为负数")
                
                # 5. 创建订单（使用模型必需字段）
                # order_time默认为当前时间，channel默认为dine_in，payment_method默认为cash
                order = OrderHeader(
                    order_no=order_no,
                    store_id=store_id,
                    biz_date=biz_date,
                    order_time=datetime.now(),  # 默认当前时间
                    channel=get_field(row, "channel", "dine_in"),  # 默认堂食
                    gross_amount=gross_amount,
                    discount_amount=discount_amount,
                    net_amount=net_amount,
                    payment_method=get_field(row, "payment_method", "cash"),  # 默认现金
                    status="completed",  # 导入的订单默认为已完成
                )
                
                db.add(order)
                existing_order_nos.add(order_no)  # 加入去重集合
                success_count += 1
            
            except Exception as e:
                # 记录错误
                error = DataImportJobError(
                    job_id=job.id,
                    row_no=idx,
                    field="",
                    message=str(e),
                    raw_data=row,
                )
                db.add(error)
                fail_count += 1
        
        # 批量提交
        await db.flush()
        
        job.success_rows = success_count
        job.fail_rows = fail_count
    
    @staticmethod
    async def _import_expense_records(db: AsyncSession, job: DataImportJob, rows: List[Dict[str, Any]]):
        """导入费用记录"""
        store_id = job.config.get("store_id")
        mapping = job.config.get("mapping", {})
        
        def get_field(row: dict, field: str, default=None):
            mapped_field = mapping.get(field, field)
            return row.get(mapped_field, default)
        
        # 预加载费用科目
        expense_types_result = await db.execute(select(ExpenseType))
        expense_types = {et.type_code: et.id for et in expense_types_result.scalars().all()}
        
        # 构建去重键集合（store_id, biz_date, expense_type_id, amount, description）
        existing_records = await db.execute(
            select(
                ExpenseRecord.store_id,
                ExpenseRecord.biz_date,
                ExpenseRecord.expense_type_id,
                ExpenseRecord.amount,
                ExpenseRecord.description
            ).where(ExpenseRecord.store_id == store_id)
        )
        
        existing_keys = set()
        for rec in existing_records.all():
            key = (rec.store_id, rec.biz_date, rec.expense_type_id, float(rec.amount), rec.description or "")
            existing_keys.add(key)
        
        success_count = 0
        fail_count = 0
        
        for idx, row in enumerate(rows, start=1):
            try:
                # 1. 提取字段
                expense_type_code = get_field(row, "expense_type_code", "").strip()
                biz_date_str = get_field(row, "biz_date", "").strip()
                amount_str = get_field(row, "amount", "")
                description = get_field(row, "description", "").strip()
                
                # 2. 必填校验
                if not expense_type_code:
                    raise ValueError("费用科目编码不能为空")
                
                if not biz_date_str:
                    raise ValueError("业务日期不能为空")
                
                if not amount_str:
                    raise ValueError("金额不能为空")
                
                # 3. 费用科目校验
                if expense_type_code not in expense_types:
                    raise ValueError(f"费用科目编码 {expense_type_code} 不存在")
                
                expense_type_id = expense_types[expense_type_code]
                
                # 4. 数据转换
                try:
                    biz_date = datetime.strptime(str(biz_date_str), "%Y-%m-%d").date()
                except ValueError:
                    raise ValueError(f"业务日期格式错误: {biz_date_str}")
                
                try:
                    amount = Decimal(str(amount_str))
                except (InvalidOperation, ValueError):
                    raise ValueError(f"金额格式错误: {amount_str}")
                
                if amount < 0:
                    raise ValueError("金额不能为负数")
                
                # 5. 幂等性检查
                dup_key = (store_id, biz_date, expense_type_id, float(amount), description)
                if dup_key in existing_keys:
                    raise ValueError("记录已存在（门店、日期、科目、金额、描述完全相同）")
                
                # 6. 创建记录
                record = ExpenseRecord(
                    store_id=store_id,
                    expense_type_id=expense_type_id,
                    biz_date=biz_date,
                    amount=amount,
                    description=description,
                )
                
                db.add(record)
                existing_keys.add(dup_key)
                success_count += 1
            
            except Exception as e:
                error = DataImportJobError(
                    job_id=job.id,
                    row_no=idx,
                    field="",
                    message=str(e),
                    raw_data=row,
                )
                db.add(error)
                fail_count += 1
        
        await db.flush()
        
        job.success_rows = success_count
        job.fail_rows = fail_count
    
    @staticmethod
    async def _import_stores(db: AsyncSession, job: DataImportJob, rows: List[Dict[str, Any]]):
        """导入门店数据"""
        # TODO: 实现门店导入逻辑
        raise BusinessException("门店导入功能暂未实现")
    
    @staticmethod
    async def _import_expense_types(db: AsyncSession, job: DataImportJob, rows: List[Dict[str, Any]]):
        """导入费用科目数据"""
        # TODO: 实现费用科目导入逻辑
        raise BusinessException("费用科目导入功能暂未实现")
    
    @staticmethod
    async def list_jobs(
        db: AsyncSession,
        filters: ImportJobFilter,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[DataImportJob], int]:
        """分页查询导入任务"""
        query = select(DataImportJob)
        
        # 构建过滤条件
        conditions = []
        if filters.target_type:
            conditions.append(DataImportJob.target_type == filters.target_type)
        
        if filters.status:
            conditions.append(DataImportJob.status == filters.status)
        
        if filters.created_by_id:
            conditions.append(DataImportJob.created_by_id == filters.created_by_id)
        
        if filters.date_from:
            conditions.append(DataImportJob.created_at >= filters.date_from)
        
        if filters.date_to:
            conditions.append(DataImportJob.created_at <= filters.date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 查询总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await db.execute(count_query)).scalar() or 0
        
        # 分页查询
        query = query.order_by(DataImportJob.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return list(jobs), total
    
    @staticmethod
    async def get_job_detail(db: AsyncSession, job_id: int) -> DataImportJob:
        """获取任务详情"""
        from sqlalchemy.orm import selectinload
        
        result = await db.execute(
            select(DataImportJob)
            .options(selectinload(DataImportJob.created_by))
            .where(DataImportJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            raise NotFoundException(f"导入任务 {job_id} 不存在")
        
        return job
    
    @staticmethod
    async def list_job_errors(
        db: AsyncSession,
        job_id: int,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[DataImportJobError], int]:
        """分页查询任务错误"""
        # 查询总数
        count_query = select(func.count()).where(DataImportJobError.job_id == job_id)
        total = (await db.execute(count_query)).scalar() or 0
        
        # 分页查询
        query = (
            select(DataImportJobError)
            .where(DataImportJobError.job_id == job_id)
            .order_by(DataImportJobError.row_no)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        
        result = await db.execute(query)
        errors = result.scalars().all()
        
        return list(errors), total
    
    @staticmethod
    async def build_error_report(db: AsyncSession, job_id: int) -> str:
        """生成错误报告文件"""
        job = await ImportService.get_job_detail(db, job_id)
        
        # 查询所有错误
        result = await db.execute(
            select(DataImportJobError)
            .where(DataImportJobError.job_id == job_id)
            .order_by(DataImportJobError.row_no)
        )
        errors = result.scalars().all()
        
        if not errors:
            return ""
        
        # 生成错误报告文件
        job_dir = Path(job.file_path).parent
        report_path = job_dir / f"error_report_{job_id}.csv"
        
        with open(report_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["行号", "错误字段", "错误信息", "原始数据"])
            
            for error in errors:
                raw_data_str = str(error.raw_data) if error.raw_data else ""
                writer.writerow([
                    error.row_no,
                    error.field or "",
                    error.message,
                    raw_data_str,
                ])
        
        # 更新任务记录
        job.error_report_path = str(report_path)
        await db.commit()
        
        return str(report_path)
