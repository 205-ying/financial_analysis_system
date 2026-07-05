"""add data import job tables

Revision ID: 0003_import_jobs
Revises: 0002_audit_log
Create Date: 2026-01-25 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0003_import_jobs'
down_revision: Union[str, None] = '0002_audit_log'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建数据导入任务相关表"""
    
    # 创建枚举类型（使用 DO 块检查是否存在）
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE import_source_type AS ENUM ('excel', 'csv');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE import_target_type AS ENUM ('orders', 'expense_records', 'stores', 'expense_types');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE import_job_status AS ENUM ('pending', 'running', 'success', 'partial_fail', 'fail');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 创建数据导入任务表
    op.create_table(
        'data_import_jobs',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('job_name', sa.String(length=200), nullable=False, comment='任务名称'),
        sa.Column('source_type', sa.Enum('excel', 'csv', name='import_source_type', create_type=False), 
                  nullable=False, comment='源文件类型 (excel/csv)'),
        sa.Column('target_type', sa.Enum('orders', 'expense_records', 'stores', 'expense_types', 
                  name='import_target_type', create_type=False), 
                  nullable=False, comment='目标数据类型'),
        sa.Column('status', sa.Enum('pending', 'running', 'success', 'partial_fail', 'fail', 
                  name='import_job_status', create_type=False), 
                  nullable=False, server_default='pending', comment='任务状态'),
        sa.Column('file_name', sa.String(length=500), nullable=False, comment='原始文件名'),
        sa.Column('file_path', sa.String(length=1000), nullable=False, comment='文件存储路径'),
        sa.Column('total_rows', sa.Integer(), nullable=False, server_default='0', comment='总行数'),
        sa.Column('success_rows', sa.Integer(), nullable=False, server_default='0', comment='成功行数'),
        sa.Column('fail_rows', sa.Integer(), nullable=False, server_default='0', comment='失败行数'),
        sa.Column('error_report_path', sa.String(length=1000), nullable=True, comment='错误报告文件路径'),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True, 
                  comment='任务配置 (映射关系、门店ID等)'),
        sa.Column('created_by_id', sa.Integer(), nullable=True, comment='创建用户ID'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ondelete='SET NULL'),
        comment='数据导入任务表'
    )
    
    # 创建索引
    op.create_index('idx_import_job_status', 'data_import_jobs', ['status'])
    op.create_index('idx_import_job_target_type', 'data_import_jobs', ['target_type'])
    op.create_index('idx_import_job_created_at', 'data_import_jobs', ['created_at'])
    op.create_index('idx_import_job_created_by', 'data_import_jobs', ['created_by_id'])
    
    # 创建数据导入错误记录表
    op.create_table(
        'data_import_job_errors',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('job_id', sa.Integer(), nullable=False, comment='任务ID'),
        sa.Column('row_no', sa.Integer(), nullable=False, comment='错误行号 (从1开始)'),
        sa.Column('field', sa.String(length=100), nullable=True, comment='错误字段'),
        sa.Column('message', sa.Text(), nullable=False, comment='错误信息'),
        sa.Column('raw_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='原始行数据'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['job_id'], ['data_import_jobs.id'], ondelete='CASCADE'),
        comment='数据导入错误记录表'
    )
    
    # 创建错误表索引
    op.create_index('idx_import_error_job_id', 'data_import_job_errors', ['job_id'])
    op.create_index('idx_import_error_row_no', 'data_import_job_errors', ['job_id', 'row_no'])


def downgrade() -> None:
    """删除数据导入任务相关表"""
    
    # 删除索引
    op.drop_index('idx_import_error_row_no', table_name='data_import_job_errors')
    op.drop_index('idx_import_error_job_id', table_name='data_import_job_errors')
    
    op.drop_index('idx_import_job_created_by', table_name='data_import_jobs')
    op.drop_index('idx_import_job_created_at', table_name='data_import_jobs')
    op.drop_index('idx_import_job_target_type', table_name='data_import_jobs')
    op.drop_index('idx_import_job_status', table_name='data_import_jobs')
    
    # 删除表
    op.drop_table('data_import_job_errors')
    op.drop_table('data_import_jobs')
    
    # 删除枚举类型
    op.execute('DROP TYPE import_job_status')
    op.execute('DROP TYPE import_target_type')
    op.execute('DROP TYPE import_source_type')
