"""add audit_log table

Revision ID: 0002_audit_log
Revises: 0001_initial
Create Date: 2026-01-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0002_audit_log'
down_revision: Union[str, None] = '0001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建审计日志表"""
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False, comment='主键ID'),
        sa.Column('user_id', sa.Integer(), nullable=True, comment='操作用户ID'),
        sa.Column('username', sa.String(length=50), nullable=False, comment='操作用户名（冗余存储，防止用户删除后无法追溯）'),
        sa.Column('action', sa.String(length=50), nullable=False, comment='操作类型：login/logout/create_expense/update_expense/delete_expense/rebuild_kpi等'),
        sa.Column('resource_type', sa.String(length=50), nullable=True, comment='资源类型：expense/kpi/order/store/user等'),
        sa.Column('resource_id', sa.Integer(), nullable=True, comment='资源ID'),
        sa.Column('detail', sa.Text(), nullable=True, comment='操作详情（JSON格式），不包含敏感信息如密码'),
        sa.Column('ip_address', sa.String(length=45), nullable=True, comment='客户端IP地址（支持IPv6）'),
        sa.Column('user_agent', sa.String(length=255), nullable=True, comment='客户端User-Agent'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='success', comment='操作结果：success/failure/error'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息（仅在失败时记录）'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        comment='审计日志表'
    )
    
    # 创建索引以提升查询性能
    op.create_index('ix_audit_log_user_id', 'audit_log', ['user_id'])
    op.create_index('ix_audit_log_action', 'audit_log', ['action'])
    op.create_index('ix_audit_log_resource_type', 'audit_log', ['resource_type'])
    op.create_index('ix_audit_log_created_at', 'audit_log', ['created_at'])
    op.create_index('ix_audit_log_id', 'audit_log', ['id'])


def downgrade() -> None:
    """删除审计日志表"""
    op.drop_index('ix_audit_log_created_at', table_name='audit_log')
    op.drop_index('ix_audit_log_resource_type', table_name='audit_log')
    op.drop_index('ix_audit_log_action', table_name='audit_log')
    op.drop_index('ix_audit_log_user_id', table_name='audit_log')
    op.drop_index('ix_audit_log_id', table_name='audit_log')
    op.drop_table('audit_log')
