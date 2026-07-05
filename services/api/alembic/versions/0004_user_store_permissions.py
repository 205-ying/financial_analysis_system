"""add_user_store_permissions

Revision ID: 0004_user_store_permissions
Revises: 0003_import_jobs
Create Date: 2026-01-26 10:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0004_user_store_permissions'
down_revision: Union[str, None] = '0003_import_jobs'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建用户门店权限表"""
    op.create_table(
        'user_store_permissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('store_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['store_id'], ['store.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'store_id', name='uix_user_store')
    )
    op.create_index(op.f('ix_user_store_permissions_id'), 'user_store_permissions', ['id'], unique=False)
    op.create_index(op.f('ix_user_store_permissions_store_id'), 'user_store_permissions', ['store_id'], unique=False)
    op.create_index(op.f('ix_user_store_permissions_user_id'), 'user_store_permissions', ['user_id'], unique=False)


def downgrade() -> None:
    """删除用户门店权限表"""
    op.drop_index(op.f('ix_user_store_permissions_user_id'), table_name='user_store_permissions')
    op.drop_index(op.f('ix_user_store_permissions_store_id'), table_name='user_store_permissions')
    op.drop_index(op.f('ix_user_store_permissions_id'), table_name='user_store_permissions')
    op.drop_table('user_store_permissions')
