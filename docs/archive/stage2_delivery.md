# 阶段二交付文档：数据库模型与迁移

## ✅ 完成状态

**所有任务已完成！**所有 14 张表已成功创建并通过验证。

---

## 📁 模型文件位置

### 核心模型文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 基础混入类 | `backend/src/app/models/base.py` | IDMixin, TimestampMixin, SoftDeleteMixin, UserTrackingMixin |
| 用户权限模型 | `backend/src/app/models/user.py` | User, Role, Permission + 关联表 |
| 门店产品模型 | `backend/src/app/models/store.py` | Store, ProductCategory, Product |
| 订单模型 | `backend/src/app/models/order.py` | OrderHeader, OrderItem |
| 费用模型 | `backend/src/app/models/expense.py` | ExpenseType, ExpenseRecord |
| KPI 和审计 | `backend/src/app/models/kpi.py` | KpiDailyStore, AuditLog |
| 模型注册 | `backend/src/app/models/__init__.py` | 导出所有模型供 Alembic 使用 |

---

## 🗂️ 数据库表结构

### 1. 用户与权限（5 张表）

#### user - 用户表
- **主键**: id (Serial)
- **唯一约束**: username, email
- **索引**: username, email
- **关键字段**: 
  - `password_hash`: 密码哈希
  - `is_active`: 是否激活
  - `is_superuser`: 是否超级用户
  - `created_at/updated_at`: 时间戳（timezone-aware）

#### role - 角色表
- **主键**: id
- **唯一约束**: code
- **索引**: code
- **关键字段**: `code`, `name`, `is_active`

#### permission - 权限表
- **主键**: id
- **唯一约束**: code
- **索引**: code
- **关键字段**: `resource`, `action` (用于 RBAC 权限控制)

#### user_role - 用户角色关联表
- **联合主键**: (user_id, role_id)
- **外键**: CASCADE 删除

#### role_permission - 角色权限关联表
- **联合主键**: (role_id, permission_id)
- **外键**: CASCADE 删除

---

### 2. 门店与产品（3 张表）

#### store - 门店表
- **主键**: id
- **唯一约束**: code
- **索引**: code
- **软删除**: deleted_at
- **关键字段**: 
  - `code`: 门店编码（唯一）
  - `area_sqm`: 营业面积（Decimal）
  - `is_active`: 是否营业

#### product_category - 产品分类表（树形结构）
- **主键**: id
- **唯一约束**: code
- **索引**: code, parent_id
- **外键**: parent_id → product_category.id (自关联)
- **关键字段**: 
  - `parent_id`: 父分类（可空）
  - `level`: 层级深度

#### product - 产品表
- **主键**: id
- **唯一约束**: sku_code
- **索引**: sku_code, category_id
- **外键**: category_id → product_category.id (RESTRICT)
- **软删除**: deleted_at
- **关键字段**: 
  - `sku_code`: SKU 编码（唯一）
  - `unit_price`: 单价（Decimal）
  - `cost_price`: 成本价（Decimal）

---

### 3. 订单（2 张表）

#### order_header - 订单主表
- **主键**: id
- **唯一约束**: order_no
- **索引**: order_no, store_id, biz_date, order_time, status
- **外键**: 
  - store_id → store.id (RESTRICT)
  - operator_id → user.id (SET NULL)
- **检查约束**: 
  - `gross_amount >= 0`
  - `net_amount >= 0`
  - `discount_amount >= 0`
- **关键字段**: 
  - `order_no`: 订单号（唯一）
  - `biz_date`: 业务日期（Date）
  - `order_time`: 下单时间（DateTime with timezone）
  - `channel`: 订单渠道（堂食/外带/外卖）
  - `status`: 订单状态（待支付/已支付/已取消）

#### order_item - 订单明细表
- **主键**: id
- **索引**: order_id, product_id
- **外键**: 
  - order_id → order_header.id (CASCADE)
  - product_id → product.id (RESTRICT)
- **检查约束**: 
  - `quantity > 0`
  - `unit_price >= 0`
  - `line_amount >= 0`
- **快照字段**: `product_sku`, `product_name`, `product_category` (订单时产品信息快照)

---

### 4. 费用（2 张表）

#### expense_type - 费用科目表（树形结构）
- **主键**: id
- **唯一约束**: type_code
- **索引**: type_code, parent_id
- **外键**: parent_id → expense_type.id (自关联)
- **关键字段**: 
  - `type_code`: 科目编码（唯一）
  - `category`: 费用类别（成本/费用）
  - `level`: 层级深度

#### expense_record - 费用记录表
- **主键**: id
- **索引**: store_id, expense_type_id, biz_date, status, created_by, invoice_no
- **外键**: 
  - store_id → store.id (RESTRICT)
  - expense_type_id → expense_type.id (RESTRICT)
  - created_by → user.id (RESTRICT)
  - approved_by → user.id (SET NULL)
- **检查约束**: `amount >= 0`
- **审批流**: `status` (草稿/待审批/已审批/已驳回)

---

### 5. KPI 与审计（2 张表）

#### kpi_daily_store - 门店日度 KPI 汇总表
- **主键**: id
- **联合唯一约束**: (biz_date, store_id)
- **索引**: biz_date, store_id
- **外键**: store_id → store.id (RESTRICT)
- **检查约束**: `revenue >= 0`, `net_revenue >= 0`
- **关键字段**: 
  - 收入类: `revenue`, `refund_amount`, `discount_amount`, `net_revenue`
  - 成本类: `cost_material`, `cost_labor`, `cost_rent`, `cost_utilities`, `cost_marketing`, `cost_other`
  - 利润类: `gross_profit`, `operating_profit`, `profit_rate`
  - 经营类: `order_count`, `customer_count`, `avg_order_value`
  - 渠道类: `dine_in_revenue`, `takeout_revenue`, `delivery_revenue`, `online_revenue`

#### audit_log - 审计日志表
- **主键**: id
- **索引**: user_id, action, resource, resource_id, ip_address, created_at
- **外键**: user_id → user.id (SET NULL)
- **PostgreSQL 特性**: `detail` 字段使用 JSONB 类型
- **关键字段**: 
  - `action`: 操作类型（CREATE/UPDATE/DELETE/LOGIN）
  - `resource`: 资源类型（user/store/order 等）
  - `detail`: 操作详情（JSONB 格式）

---

## 🔑 关键约束说明

### 唯一约束 (Unique Constraints)
```sql
-- 用户
uq_user_username, uq_user_email

-- 角色权限
uq_role_code, uq_permission_code

-- 门店产品
uq_store_code, uq_product_category_code, uq_product_sku_code

-- 订单费用
uq_order_header_order_no, uq_expense_type_code

-- KPI
uq_kpi_daily_store_date_store (biz_date + store_id 联合唯一)
```

### 外键约束 (Foreign Keys)
```sql
-- 关键业务外键（RESTRICT 防止误删）
product.category_id → product_category.id
order_header.store_id → store.id
order_item.product_id → product.id
expense_record.store_id → store.id
expense_record.expense_type_id → expense_type.id

-- 级联删除（CASCADE 自动清理关联数据）
order_item.order_id → order_header.id
user_role.user_id/role_id → user.id/role.id
role_permission.role_id/permission_id → role.id/permission.id
```

### 检查约束 (Check Constraints)
```sql
-- 金额非负
ck_order_header_gross_amount: gross_amount >= 0
ck_order_header_net_amount: net_amount >= 0
ck_order_item_unit_price: unit_price >= 0
ck_expense_record_amount: amount >= 0
ck_kpi_daily_store_revenue: revenue >= 0

-- 数量正数
ck_order_item_quantity: quantity > 0
```

### 索引 (Indexes)
```sql
-- 业务查询高频索引
ix_order_header_biz_date, ix_order_header_store_id, ix_order_header_status
ix_expense_record_biz_date, ix_expense_record_store_id, ix_expense_record_status
ix_kpi_daily_store_biz_date, ix_kpi_daily_store_store_id

-- 唯一性查询索引
ix_user_username, ix_user_email
ix_store_code, ix_product_sku_code, ix_order_header_order_no
```

---

## 🗃️ 迁移文件

| 文件 | 路径 | 说明 |
|------|------|------|
| 初始化迁移 | `backend/alembic/versions/0001_initial.py` | 创建所有 14 张表 |
| Alembic 配置 | `backend/alembic.ini` | 数据库连接配置 |
| 迁移环境 | `backend/alembic/env.py` | 异步迁移支持 |

### 迁移脚本特性
- ✅ **异步支持**: 使用 asyncpg 驱动
- ✅ **事务安全**: DDL 包装在事务中
- ✅ **自动注释**: 所有表和列都有中文注释
- ✅ **升级/降级**: 完整的 upgrade/downgrade 函数

---

## 🌱 初始化脚本

### 种子数据脚本
**位置**: `backend/scripts/seed_data.py`

**功能**:
- 🔐 **用户权限**: 创建 24 个权限、4 个角色、3 个测试用户
- 🏪 **门店数据**: 创建 3 个门店（中关村店、三里屯店、望京店）
- 📁 **产品分类**: 创建 2 级分类树（食品、饮品及其子分类）
- 🍱 **产品数据**: 创建 8 个产品（盖饭、面条、饮料等）
- 💰 **费用科目**: 创建 2 级费用科目树（原材料、人工、租金等）

**测试账号**:
```
管理员: admin / Admin@123 (拥有所有权限)
门店经理: manager / Manager@123 (门店运营权限)
收银员: cashier / Cashier@123 (订单处理权限)
```

### 约束验证脚本
**位置**: `backend/scripts/verify_constraints.py`

**验证项**:
- ✅ 表结构完整性（14 张表）
- ✅ 唯一约束（10 个）
- ✅ 外键约束（9 个关键外键）
- ✅ 索引完整性（13 个关键索引）
- ✅ 检查约束（6 个金额/数量约束）
- ✅ 列类型正确性（timezone、date、numeric、jsonb）

---

## ✅ 验收命令

### 1. 执行迁移
```bash
cd backend
alembic upgrade head
```
**预期输出**: 
```
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial, initial database schema
```

### 2. 验证约束
```bash
python scripts/verify_constraints.py
```
**预期输出**: 所有验证项显示 ✅

### 3. 初始化种子数据
```bash
python scripts/seed_data.py
```
**预期输出**: 
```
✅ 创建了 24 个权限
✅ 创建了 4 个角色
✅ 创建了 3 个用户
✅ 创建了 3 个门店
✅ 创建了 8 个产品
✅ 创建了 12 个费用科目
```

### 4. 数据库验证（psql）
```bash
# 查看所有表
psql -U postgres -d financial_analysis -c "\dt"

# 验证唯一约束
psql -U postgres -d financial_analysis -c "
SELECT constraint_name, table_name 
FROM information_schema.table_constraints 
WHERE constraint_type = 'UNIQUE' 
ORDER BY table_name;
"

# 验证外键
psql -U postgres -d financial_analysis -c "
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name;
"

# 验证索引
psql -U postgres -d financial_analysis -c "
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename;
"

# 验证数据
psql -U postgres -d financial_analysis -c "SELECT COUNT(*) FROM \"user\";"
psql -U postgres -d financial_analysis -c "SELECT code, name FROM store;"
psql -U postgres -d financial_analysis -c "SELECT sku_code, name FROM product;"
```

---

## 🎯 技术亮点

### 1. SQLAlchemy 2.0 新特性
- ✅ **类型提示**: `Mapped[int]`, `Mapped[str]` 完整类型支持
- ✅ **声明式语法**: 使用 `mapped_column()` 替代 `Column()`
- ✅ **异步支持**: 全面使用 `AsyncSession`

### 2. PostgreSQL 特性
- ✅ **时区感知**: `DateTime(timezone=True)` 所有时间戳
- ✅ **JSONB**: `audit_log.detail` 使用 JSONB 类型
- ✅ **事务 DDL**: Alembic 迁移包装在事务中

### 3. 设计模式
- ✅ **Mixin 复用**: IDMixin, TimestampMixin, SoftDeleteMixin
- ✅ **软删除**: Store, Product 使用 `deleted_at`
- ✅ **快照模式**: OrderItem 保存产品快照字段
- ✅ **树形结构**: ProductCategory, ExpenseType 使用 `parent_id` 自关联
- ✅ **审批流**: ExpenseRecord 包含 `status`, `approved_by`, `approved_at`
- ✅ **用户追踪**: ExpenseRecord 记录 `created_by`

### 4. 数据完整性
- ✅ **NOT NULL**: 关键业务字段强制非空
- ✅ **唯一约束**: 业务编码字段（code, sku_code, order_no）
- ✅ **外键约束**: 业务表使用 RESTRICT 防止误删，关联表使用 CASCADE
- ✅ **检查约束**: 金额非负、数量正数
- ✅ **联合唯一**: KPI 表使用 (biz_date, store_id) 防止重复

---

## 📊 数据库 ER 图概览

```
用户权限域:
User ←→ user_role ←→ Role ←→ role_permission ←→ Permission

门店产品域:
Store
ProductCategory (树形) → Product

订单域:
Store → OrderHeader → OrderItem ← Product
         ↓
        User (operator_id)

费用域:
ExpenseType (树形)
         ↓
ExpenseRecord ← Store
         ↓
        User (created_by, approved_by)

KPI 域:
Store → KpiDailyStore

审计域:
User → AuditLog
```

---

## 🚀 下一步建议

### 阶段三：API 实现
1. **CRUD 接口**: 为所有模型实现增删改查接口
2. **认证授权**: JWT 登录、RBAC 权限中间件
3. **数据校验**: Pydantic Schemas
4. **查询优化**: 分页、排序、过滤

### 阶段四：业务逻辑
1. **订单处理**: 下单、支付、退款流程
2. **费用审批**: 提交、审批、驳回工作流
3. **KPI 计算**: 日度汇总定时任务
4. **审计日志**: 中间件自动记录操作

### 阶段五：前端集成
1. **Vue3 + TypeScript**: 类型安全的前端
2. **Element Plus**: 企业级组件库
3. **ECharts**: KPI 数据可视化
4. **Pinia**: 状态管理

---

## 📝 注意事项

1. **密码加密**: 使用 bcrypt 加密，最大长度 72 字节
2. **时区处理**: 所有 DateTime 字段使用 timezone-aware
3. **软删除**: Store, Product 使用 `deleted_at`，查询时需过滤
4. **树形结构**: 递归查询需注意性能，考虑使用 CTE 或物化路径
5. **JSONB 索引**: 如需频繁查询 `audit_log.detail`，考虑添加 GIN 索引
6. **外键级联**: 注意 CASCADE vs RESTRICT 的使用场景

---

## ✅ 验收结果

**日期**: 2026-01-22  
**状态**: ✅ 全部通过

- ✅ 14 张表全部创建成功
- ✅ 10 个唯一约束全部验证通过
- ✅ 9 个关键外键全部验证通过
- ✅ 13 个关键索引全部验证通过
- ✅ 6 个检查约束全部验证通过
- ✅ 所有列类型正确（timezone、jsonb、numeric）
- ✅ 种子数据初始化成功（3 用户、3 门店、8 产品、12 科目）

**Alembic 迁移版本**: `0001_initial`  
**数据库版本**: PostgreSQL 14+  
**SQLAlchemy 版本**: 2.0.23
