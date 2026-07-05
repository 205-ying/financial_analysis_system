"""initial database schema

Revision ID: 0001_initial
Revises: 
Create Date: 2026-01-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### 创建用户和权限表 ###
    
    # 用户表
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('username', sa.String(length=50), nullable=False, comment='用户名'),
    sa.Column('email', sa.String(length=100), nullable=False, comment='邮箱'),
    sa.Column('password_hash', sa.String(length=255), nullable=False, comment='密码哈希'),
    sa.Column('full_name', sa.String(length=100), nullable=True, comment='真实姓名'),
    sa.Column('phone', sa.String(length=20), nullable=True, comment='手机号'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否激活'),
    sa.Column('is_superuser', sa.Boolean(), nullable=False, comment='是否超级用户'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user')),
    sa.UniqueConstraint('email', name=op.f('uq_user_email')),
    sa.UniqueConstraint('username', name=op.f('uq_user_username')),
    comment='用户表'
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=False)
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=False)
    
    # 角色表
    op.create_table('role',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('code', sa.String(length=50), nullable=False, comment='角色编码'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='角色名称'),
    sa.Column('description', sa.Text(), nullable=True, comment='角色描述'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否启用'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_role')),
    sa.UniqueConstraint('code', name=op.f('uq_role_code')),
    comment='角色表'
    )
    op.create_index(op.f('ix_role_code'), 'role', ['code'], unique=False)
    
    # 权限表
    op.create_table('permission',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('code', sa.String(length=100), nullable=False, comment='权限编码'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='权限名称'),
    sa.Column('resource', sa.String(length=100), nullable=False, comment='资源标识'),
    sa.Column('action', sa.String(length=50), nullable=False, comment='操作类型'),
    sa.Column('description', sa.Text(), nullable=True, comment='权限描述'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_permission')),
    sa.UniqueConstraint('code', name=op.f('uq_permission_code')),
    comment='权限表'
    )
    op.create_index(op.f('ix_permission_code'), 'permission', ['code'], unique=False)
    
    # 用户角色关联表
    op.create_table('user_role',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'role_id'),
    comment='用户角色关联表'
    )
    
    # 角色权限关联表
    op.create_table('role_permission',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permission.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    comment='角色权限关联表'
    )
    
    # ### 创建门店和产品表 ###
    
    # 门店表
    op.create_table('store',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('code', sa.String(length=50), nullable=False, comment='门店编码'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='门店名称'),
    sa.Column('address', sa.String(length=200), nullable=True, comment='门店地址'),
    sa.Column('phone', sa.String(length=20), nullable=True, comment='联系电话'),
    sa.Column('contact_person', sa.String(length=50), nullable=True, comment='联系人'),
    sa.Column('business_hours', sa.String(length=100), nullable=True, comment='营业时间'),
    sa.Column('area_sqm', sa.Numeric(precision=10, scale=2), nullable=True, comment='营业面积（平方米）'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否营业'),
    sa.Column('sort_order', sa.Integer(), nullable=False, comment='排序顺序'),
    sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False, comment='是否已删除'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_store')),
    sa.UniqueConstraint('code', name=op.f('uq_store_code')),
    comment='门店表'
    )
    op.create_index(op.f('ix_store_code'), 'store', ['code'], unique=False)
    
    # 产品分类表
    op.create_table('product_category',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('code', sa.String(length=50), nullable=False, comment='分类编码'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='分类名称'),
    sa.Column('parent_id', sa.Integer(), nullable=True, comment='父分类ID'),
    sa.Column('level', sa.Integer(), nullable=False, comment='层级'),
    sa.Column('description', sa.Text(), nullable=True, comment='分类描述'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否启用'),
    sa.Column('sort_order', sa.Integer(), nullable=False, comment='排序顺序'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.ForeignKeyConstraint(['parent_id'], ['product_category.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_product_category')),
    sa.UniqueConstraint('code', name=op.f('uq_product_category_code')),
    comment='产品分类表'
    )
    op.create_index(op.f('ix_product_category_code'), 'product_category', ['code'], unique=False)
    op.create_index(op.f('ix_product_category_parent_id'), 'product_category', ['parent_id'], unique=False)
    
    # 产品表
    op.create_table('product',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('sku_code', sa.String(length=50), nullable=False, comment='SKU编码'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='产品名称'),
    sa.Column('category_id', sa.Integer(), nullable=False, comment='分类ID'),
    sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False, comment='单价'),
    sa.Column('cost_price', sa.Numeric(precision=10, scale=2), nullable=True, comment='成本价'),
    sa.Column('unit', sa.String(length=20), nullable=False, comment='单位'),
    sa.Column('description', sa.Text(), nullable=True, comment='产品描述'),
    sa.Column('image_url', sa.String(length=500), nullable=True, comment='产品图片URL'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否在售'),
    sa.Column('is_featured', sa.Boolean(), nullable=False, comment='是否推荐'),
    sa.Column('sort_order', sa.Integer(), nullable=False, comment='排序顺序'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='删除时间'),
    sa.ForeignKeyConstraint(['category_id'], ['product_category.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_product')),
    sa.UniqueConstraint('sku_code', name=op.f('uq_product_sku_code')),
    comment='产品表'
    )
    op.create_index(op.f('ix_product_category_id'), 'product', ['category_id'], unique=False)
    op.create_index(op.f('ix_product_sku_code'), 'product', ['sku_code'], unique=False)
    
    # ### 创建订单表 ###
    
    # 订单主表
    op.create_table('order_header',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('order_no', sa.String(length=50), nullable=False, comment='订单号'),
    sa.Column('store_id', sa.Integer(), nullable=False, comment='门店ID'),
    sa.Column('biz_date', sa.Date(), nullable=False, comment='业务日期'),
    sa.Column('order_time', sa.DateTime(timezone=True), nullable=False, comment='下单时间'),
    sa.Column('channel', sa.String(length=20), nullable=False, comment='订单渠道'),
    sa.Column('table_no', sa.String(length=20), nullable=True, comment='桌号'),
    sa.Column('gross_amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='商品总额'),
    sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='优惠金额'),
    sa.Column('service_charge', sa.Numeric(precision=10, scale=2), nullable=False, comment='服务费'),
    sa.Column('delivery_fee', sa.Numeric(precision=10, scale=2), nullable=False, comment='配送费'),
    sa.Column('net_amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='实收金额'),
    sa.Column('payment_method', sa.String(length=20), nullable=False, comment='支付方式'),
    sa.Column('payment_time', sa.DateTime(timezone=True), nullable=True, comment='支付时间'),
    sa.Column('status', sa.String(length=20), nullable=False, comment='订单状态'),
    sa.Column('customer_name', sa.String(length=50), nullable=True, comment='客户姓名'),
    sa.Column('customer_phone', sa.String(length=20), nullable=True, comment='客户电话'),
    sa.Column('customer_address', sa.String(length=200), nullable=True, comment='客户地址'),
    sa.Column('remark', sa.Text(), nullable=True, comment='订单备注'),
    sa.Column('operator_id', sa.Integer(), nullable=True, comment='操作员ID'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.CheckConstraint('discount_amount >= 0', name=op.f('ck_order_header_discount_amount')),
    sa.CheckConstraint('gross_amount >= 0', name=op.f('ck_order_header_gross_amount')),
    sa.CheckConstraint('net_amount >= 0', name=op.f('ck_order_header_net_amount')),
    sa.ForeignKeyConstraint(['operator_id'], ['user.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['store_id'], ['store.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_order_header')),
    sa.UniqueConstraint('order_no', name=op.f('uq_order_header_order_no')),
    comment='订单主表'
    )
    op.create_index(op.f('ix_order_header_biz_date'), 'order_header', ['biz_date'], unique=False)
    op.create_index(op.f('ix_order_header_order_no'), 'order_header', ['order_no'], unique=False)
    op.create_index(op.f('ix_order_header_order_time'), 'order_header', ['order_time'], unique=False)
    op.create_index(op.f('ix_order_header_status'), 'order_header', ['status'], unique=False)
    op.create_index(op.f('ix_order_header_store_id'), 'order_header', ['store_id'], unique=False)
    
    # 订单明细表
    op.create_table('order_item',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('order_id', sa.Integer(), nullable=False, comment='订单ID'),
    sa.Column('product_id', sa.Integer(), nullable=False, comment='产品ID'),
    sa.Column('product_sku', sa.String(length=50), nullable=False, comment='产品SKU（快照）'),
    sa.Column('product_name', sa.String(length=100), nullable=False, comment='产品名称（快照）'),
    sa.Column('product_category', sa.String(length=100), nullable=True, comment='产品分类（快照）'),
    sa.Column('quantity', sa.Numeric(precision=10, scale=3), nullable=False, comment='数量'),
    sa.Column('unit', sa.String(length=20), nullable=False, comment='单位'),
    sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False, comment='单价'),
    sa.Column('line_amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='小计金额'),
    sa.Column('discount_amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='优惠金额'),
    sa.Column('remark', sa.String(length=200), nullable=True, comment='商品备注'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.CheckConstraint('line_amount >= 0', name=op.f('ck_order_item_line_amount')),
    sa.CheckConstraint('quantity > 0', name=op.f('ck_order_item_quantity')),
    sa.CheckConstraint('unit_price >= 0', name=op.f('ck_order_item_unit_price')),
    sa.ForeignKeyConstraint(['order_id'], ['order_header.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_order_item')),
    comment='订单明细表'
    )
    op.create_index(op.f('ix_order_item_order_id'), 'order_item', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_item_product_id'), 'order_item', ['product_id'], unique=False)
    
    # ### 创建费用表 ###
    
    # 费用科目表
    op.create_table('expense_type',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('type_code', sa.String(length=50), nullable=False, comment='费用科目编码'),
    sa.Column('name', sa.String(length=100), nullable=False, comment='费用科目名称'),
    sa.Column('parent_id', sa.Integer(), nullable=True, comment='父科目ID'),
    sa.Column('level', sa.Integer(), nullable=False, comment='科目层级'),
    sa.Column('category', sa.String(length=50), nullable=False, comment='费用类别'),
    sa.Column('description', sa.Text(), nullable=True, comment='科目描述'),
    sa.Column('is_active', sa.Boolean(), nullable=False, comment='是否启用'),
    sa.Column('sort_order', sa.Integer(), nullable=False, comment='排序顺序'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.ForeignKeyConstraint(['parent_id'], ['expense_type.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_expense_type')),
    sa.UniqueConstraint('type_code', name=op.f('uq_expense_type_code')),
    comment='费用科目表'
    )
    op.create_index(op.f('ix_expense_type_parent_id'), 'expense_type', ['parent_id'], unique=False)
    op.create_index(op.f('ix_expense_type_type_code'), 'expense_type', ['type_code'], unique=False)
    
    # 费用记录表
    op.create_table('expense_record',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('store_id', sa.Integer(), nullable=False, comment='门店ID'),
    sa.Column('expense_type_id', sa.Integer(), nullable=False, comment='费用科目ID'),
    sa.Column('biz_date', sa.Date(), nullable=False, comment='业务日期'),
    sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False, comment='费用金额'),
    sa.Column('description', sa.Text(), nullable=True, comment='费用说明'),
    sa.Column('invoice_no', sa.String(length=50), nullable=True, comment='发票号码'),
    sa.Column('vendor', sa.String(length=100), nullable=True, comment='供应商'),
    sa.Column('payment_method', sa.String(length=20), nullable=True, comment='支付方式'),
    sa.Column('payment_account', sa.String(length=100), nullable=True, comment='支付账户'),
    sa.Column('status', sa.String(length=20), nullable=False, comment='状态'),
    sa.Column('submitted_at', sa.Date(), nullable=True, comment='提交日期'),
    sa.Column('approved_at', sa.Date(), nullable=True, comment='审批日期'),
    sa.Column('approved_by', sa.Integer(), nullable=True, comment='审批人ID'),
    sa.Column('created_by', sa.Integer(), nullable=False, comment='创建人ID'),
    sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.CheckConstraint('amount >= 0', name=op.f('ck_expense_record_amount')),
    sa.ForeignKeyConstraint(['approved_by'], ['user.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['expense_type_id'], ['expense_type.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['store_id'], ['store.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_expense_record')),
    comment='费用记录表'
    )
    op.create_index(op.f('ix_expense_record_biz_date'), 'expense_record', ['biz_date'], unique=False)
    op.create_index(op.f('ix_expense_record_created_by'), 'expense_record', ['created_by'], unique=False)
    op.create_index(op.f('ix_expense_record_expense_type_id'), 'expense_record', ['expense_type_id'], unique=False)
    op.create_index(op.f('ix_expense_record_invoice_no'), 'expense_record', ['invoice_no'], unique=False)
    op.create_index(op.f('ix_expense_record_status'), 'expense_record', ['status'], unique=False)
    op.create_index(op.f('ix_expense_record_store_id'), 'expense_record', ['store_id'], unique=False)
    
    # ### 创建 KPI 和审计日志表 ###
    
    # KPI 日度汇总表
    op.create_table('kpi_daily_store',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('biz_date', sa.Date(), nullable=False, comment='业务日期'),
    sa.Column('store_id', sa.Integer(), nullable=False, comment='门店ID'),
    sa.Column('revenue', sa.Numeric(precision=12, scale=2), nullable=False, comment='营业收入（gross）'),
    sa.Column('refund_amount', sa.Numeric(precision=12, scale=2), nullable=False, comment='退款金额'),
    sa.Column('discount_amount', sa.Numeric(precision=12, scale=2), nullable=False, comment='优惠金额'),
    sa.Column('net_revenue', sa.Numeric(precision=12, scale=2), nullable=False, comment='净收入'),
    sa.Column('cost_total', sa.Numeric(precision=12, scale=2), nullable=False, comment='总成本'),
    sa.Column('cost_material', sa.Numeric(precision=12, scale=2), nullable=False, comment='原材料成本'),
    sa.Column('cost_labor', sa.Numeric(precision=12, scale=2), nullable=False, comment='人工成本'),
    sa.Column('cost_rent', sa.Numeric(precision=12, scale=2), nullable=False, comment='租金成本'),
    sa.Column('cost_utilities', sa.Numeric(precision=12, scale=2), nullable=False, comment='水电煤成本'),
    sa.Column('cost_marketing', sa.Numeric(precision=12, scale=2), nullable=False, comment='营销成本'),
    sa.Column('cost_other', sa.Numeric(precision=12, scale=2), nullable=False, comment='其他成本'),
    sa.Column('gross_profit', sa.Numeric(precision=12, scale=2), nullable=False, comment='毛利润'),
    sa.Column('operating_profit', sa.Numeric(precision=12, scale=2), nullable=False, comment='营业利润'),
    sa.Column('profit_rate', sa.Numeric(precision=5, scale=4), nullable=False, comment='利润率'),
    sa.Column('order_count', sa.Integer(), nullable=False, comment='订单数'),
    sa.Column('customer_count', sa.Integer(), nullable=False, comment='客户数'),
    sa.Column('avg_order_value', sa.Numeric(precision=10, scale=2), nullable=False, comment='客单价'),
    sa.Column('dine_in_revenue', sa.Numeric(precision=12, scale=2), nullable=False, comment='堂食收入'),
    sa.Column('takeout_revenue', sa.Numeric(precision=12, scale=2), nullable=False, comment='外带收入'),
    sa.Column('delivery_revenue', sa.Numeric(precision=12, scale=2), nullable=False, comment='外卖收入'),
    sa.Column('online_revenue', sa.Numeric(precision=12, scale=2), nullable=False, comment='线上收入'),
    sa.Column('remark', sa.Text(), nullable=True, comment='备注'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='更新时间'),
    sa.CheckConstraint('net_revenue >= 0', name=op.f('ck_kpi_daily_store_net_revenue')),
    sa.CheckConstraint('revenue >= 0', name=op.f('ck_kpi_daily_store_revenue')),
    sa.ForeignKeyConstraint(['store_id'], ['store.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_kpi_daily_store')),
    sa.UniqueConstraint('biz_date', 'store_id', name=op.f('uq_kpi_daily_store_date_store')),
    comment='门店日度 KPI 汇总表'
    )
    op.create_index(op.f('ix_kpi_daily_store_biz_date'), 'kpi_daily_store', ['biz_date'], unique=False)
    op.create_index(op.f('ix_kpi_daily_store_store_id'), 'kpi_daily_store', ['store_id'], unique=False)
    
    # 审计日志表
    op.create_table('audit_log',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='主键ID'),
    sa.Column('user_id', sa.Integer(), nullable=True, comment='用户ID'),
    sa.Column('username', sa.String(length=50), nullable=True, comment='用户名（快照）'),
    sa.Column('action', sa.String(length=50), nullable=False, comment='操作类型'),
    sa.Column('resource', sa.String(length=100), nullable=False, comment='资源类型'),
    sa.Column('resource_id', sa.String(length=100), nullable=True, comment='资源ID'),
    sa.Column('method', sa.String(length=10), nullable=True, comment='HTTP 方法'),
    sa.Column('path', sa.String(length=500), nullable=True, comment='请求路径'),
    sa.Column('ip_address', sa.String(length=50), nullable=True, comment='IP 地址'),
    sa.Column('user_agent', sa.String(length=500), nullable=True, comment='User Agent'),
    sa.Column('detail', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='操作详情（JSON）'),
    sa.Column('status_code', sa.Integer(), nullable=True, comment='响应状态码'),
    sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False, comment='创建时间'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_audit_log')),
    comment='审计日志表'
    )
    op.create_index(op.f('ix_audit_log_action'), 'audit_log', ['action'], unique=False)
    op.create_index(op.f('ix_audit_log_created_at'), 'audit_log', ['created_at'], unique=False)
    op.create_index(op.f('ix_audit_log_ip_address'), 'audit_log', ['ip_address'], unique=False)
    op.create_index(op.f('ix_audit_log_resource'), 'audit_log', ['resource'], unique=False)
    op.create_index(op.f('ix_audit_log_resource_id'), 'audit_log', ['resource_id'], unique=False)
    op.create_index(op.f('ix_audit_log_user_id'), 'audit_log', ['user_id'], unique=False)


def downgrade() -> None:
    # ### 删除所有表 ###
    op.drop_table('audit_log')
    op.drop_table('kpi_daily_store')
    op.drop_table('expense_record')
    op.drop_table('expense_type')
    op.drop_table('order_item')
    op.drop_table('order_header')
    op.drop_table('product')
    op.drop_table('product_category')
    op.drop_table('store')
    op.drop_table('role_permission')
    op.drop_table('user_role')
    op.drop_table('permission')
    op.drop_table('role')
    op.drop_table('user')