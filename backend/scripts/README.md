# Backend Scripts 说明文档

本目录包含后端维护、测试和数据管理脚本。

---

## 📁 目录结构

```
scripts/
├── seed_data.py                      # 初始化种子数据（核心脚本）⭐
├── export_api_docs.py                # 导出 OpenAPI 文档（JSON/Markdown）⭐
├── generate_bulk_data.py             # 生成批量测试数据
├── clean_bulk_data.py                # 清理批量测试数据
├── generate_import_test_data.py      # 生成导入测试数据
├── add_data_scope_permission.py      # 添加数据权限到数据库
├── list_users.py                     # 列出所有用户
├── check_import_db.py                # 检查导入数据库状态
├── test_import_e2e.py                # 导入功能端到端测试
├── verify_frontend_import.py         # 验证前端导入功能
├── verify_import_feature.py          # 验证导入功能完整性
├── verify_reports.py                 # 验证报表功能
├── maintenance/                      # 数据库维护脚本
│   ├── add_audit_permission.py
│   ├── add_soft_delete_columns.py
│   ├── fix_audit_log_table.py
│   ├── fix_detail_column.py
│   ├── fix_resource_column.py
│   └── mark_migration_done.py
├── testing/                          # 测试和检查脚本
│   ├── check_audit_data.py
│   ├── check_audit_table.py
│   ├── check_users.py
│   ├── simple_password_test.py
│   └── test_password.py
└── test_data_import/                 # 导入测试数据文件
    ├── *.csv                         # CSV测试文件
    ├── *.xlsx                        # Excel测试文件
    └── README.md
```

---

## 🚀 核心脚本

### seed_data.py - 初始化种子数据
**用途**: 首次部署时初始化系统基础数据

**功能**:
- 创建默认用户（admin, manager, cashier）
- 初始化权限和角色
- 创建示例门店
- 创建产品分类和产品
- 创建费用类型

**使用方法**:
```bash
cd backend
python scripts/seed_data.py
```

**注意事项**:
- ⚠️ 运行前确保已执行数据库迁移 (`alembic upgrade head`)
- ⚠️ 脚本会检查数据是否已存在，避免重复创建
- ✅ 默认密码：Admin@123, Manager@123, Cashier@123

---

### export_api_docs.py - 导出 OpenAPI 文档 ⭐
**用途**: 导出完整的 API 文档（OpenAPI 3.1.0 规范），用于论文和开发文档

**功能**:
- 导出 OpenAPI JSON 规范（openapi.json）
- 生成 Markdown 格式的 API 文档（api-documentation.md）
- 支持详细输出模式（显示端点和模型统计）

**使用方法**:
```bash
cd backend

# 导出 JSON 格式
python scripts/export_api_docs.py --format json

# 导出 Markdown 格式
python scripts/export_api_docs.py --format markdown

# 同时导出两种格式（推荐）
python scripts/export_api_docs.py --format both

# 详细输出模式
python scripts/export_api_docs.py --format both --verbose
```

**输出位置**:
- `backend/openapi.json` - OpenAPI 3.1.0 规范（包含40个端点，45个模型）
- `backend/api-documentation.md` - Markdown 格式的完整 API 文档

**适用场景**:
- 📄 论文附录：提供完整的 API 接口规范
- 📚 开发文档：团队协作和接口对接
- 🔄 版本管理：记录 API 变更历史
- 🧪 API 测试：可导入 Postman/Swagger UI 等工具

---

### generate_bulk_data.py - 生成批量测试数据 ⭐
**用途**: 生成大量真实、详细的中文测试数据，用于性能测试、功能验证和演示

**核心特点**:
- 📊 **数据量大**: 一年365天完整数据，50,000+订单
- 🍱 **真实菜品**: 72个真实中餐菜品（川菜、粤菜、家常菜等）
- 🕐 **时间分布**: 真实的午晚餐高峰期模拟
- 💰 **详细费用**: 包含供应商名称、采购描述、发票号
- 🏪 **门店覆盖**: 15个北京各大商圈门店
- 👥 **用户角色**: 30个不同角色用户（收银员、经理、会计）

**生成数据统计**:
- 用户：30个（收银员、经理、会计）
- 门店：15个（覆盖中关村、三里屯、国贸等商圈）
- 产品：72个（真实中餐菜品，7大分类）
- 订单：50,000+个（包含订单头和明细）
- 费用记录：7,000+条（含详细描述和供应商）
- KPI记录：5,400+条（每日每店自动计算）
- 时间范围：完整365天（一整年数据）

**真实菜品分类**（72个菜品）:
1. **川菜**（12个）：宫保鸡丁、麻婆豆腐、水煮鱼、回锅肉等
2. **粤菜**（9个）：白切鸡、烧鹅、蜜汁叉烧、清蒸鲈鱼等
3. **家常菜**（12个）：番茄炒蛋、青椒肉丝、红烧肉等
4. **凉菜**（9个）：拍黄瓜、凉拌三丝、皮蛋豆腐等
5. **面点**（12个）：牛肉面、炸酱面、小笼包、煎饺等
6. **汤品**（6个）：酸辣汤、玉米排骨汤、老鸭汤等
7. **饮品**（12个）：珍珠奶茶、鲜榨橙汁、可乐等

**订单特点**:
- 时间分布：午餐高峰（11:00-14:00）60%，晚餐高峰（17:00-21:00）30%
- 订单渠道：堂食60%，外卖30%，自提10%
- 菜品组合：简单餐、套餐、豪华餐三种类型
- 支付方式：支付宝40%，微信40%，现金15%，银行卡5%
- 周末订单量比工作日多50%

**费用记录细节**:
- 食材采购：含供应商名称（新发地、物美等）和采购明细
- 饮料采购：含品牌商（康师傅、可口可乐等）
- 工资支出：含员工数量和计算说明
- 房租费用：含面积和单价明细
- 水电费、清洁用品等日常费用
- 所有费用含发票号和详细描述

**使用方法**:
```bash
cd backend
python scripts/generate_bulk_data.py
```

**运行时间**: 约3-5分钟（取决于机器性能）

**输出示例**:
```
======================================================================
✅ 数据生成完成！
======================================================================

📊 数据统计：
  - 用户数：30 个
  - 门店数：15 个
  - 产品数：72 个（真实菜品）
  - 订单数：50,067 个
  - 费用记录：7,163 条
  - KPI记录：5,475 条
  - 时间范围：2025-02-10 至 2026-02-10

💡 提示：
  - 所有新用户的默认密码为: Test@123
  - 订单时间分布包含午餐和晚餐高峰期
  - 费用记录包含详细的供应商和描述信息
  - 菜品包含川菜、粤菜、家常菜、凉菜、面点、汤品、饮品等多个类别
```

**测试账号**:
- 收银员：cashier001~cashier018，密码：Test@123
- 经理：manager001~manager009，密码：Test@123
- 会计：accountant001~accountant003，密码：Test@123

**详细文档**: 参见 [测试数据说明.md](./测试数据说明.md)

**配置修改**:
可在脚本的 `main()` 函数中修改配置：
```python
config = {
    "users": 30,      # 用户数量
    "stores": 15,     # 门店数量
    "days": 365       # 数据天数
}
```

---

### clean_bulk_data.py - 清理批量测试数据
**用途**: 清理测试数据，恢复干净环境

**清理内容**:
- 🗑️ 订单明细（所有订单项）
- 🗑️ 订单主表（所有订单）
- 🗑️ KPI记录（所有KPI数据）
- 🗑️ 费用记录（所有费用）
- 🗑️ 产品数据（所有产品）
- 🗑️ 门店数据（所有门店）
- 🗑️ 测试用户（保留admin）

**保留内容**:
- ✅ admin用户
- ✅ 角色和权限配置
- ✅ 产品分类
- ✅ 费用科目

**使用方法**:
```bash
cd backend
python scripts/clean_bulk_data.py
```

**运行时间**: 约10-30秒

**输出示例**:
```
======================================================================
🗑️  开始清理数据库...
======================================================================

📋 清理订单明细...
  ✅ 删除了 34,080 条订单明细
📋 清理订单...
  ✅ 删除了 20,543 条订单
📊 清理KPI数据...
  ✅ 删除了 1,800 条KPI记录
💰 清理费用记录...
  ✅ 删除了 2,960 条费用记录
🍱 清理产品...
  ✅ 删除了 60 个产品
🏪 清理门店...
  ✅ 删除了 10 个门店
👤 清理用户（保留admin）...
  ✅ 删除了 20 个用户

======================================================================
✅ 数据清理完成！
======================================================================
```

**安全性**:
- ✅ 只删除业务数据，不影响基础配置
- ✅ 保留admin用户，避免无法登录
- ✅ 保留角色权限配置
- ✅ 执行前显示确认信息

**典型使用场景**:
1. 重新生成测试数据前清理旧数据
2. 性能测试前恢复初始状态
3. 演示环境数据重置
4. 开发环境数据清理

---

### generate_import_test_data.py - 生成导入测试数据
**用途**: 生成数据导入功能的测试CSV/Excel文件

**功能**:
- 生成门店导入测试数据
- 生成订单导入测试数据
- 生成费用记录导入测试数据
- 生成费用类型导入测试数据

**使用方法**:
```bash
cd backend
python scripts/generate_import_test_data.py
```

**输出位置**: `scripts/test_data_import/` 目录下的 CSV 和 Excel 文件

---

### verify_import_feature.py - 验证导入功能
**用途**: 验证数据导入中心功能完整性

**使用方法**:
```bash
cd backend
python scripts/verify_import_feature.py
```

---

### verify_reports.py - 验证报表功能
**用途**: 验证报表中心功能完整性

**使用方法**:
```bash
cd backend
python scripts/verify_reports.py
```

---

### verify_frontend_import.py - 验证前端导入功能
**用途**: 验证前端导入页面和API集成

**使用方法**:
```bash
cd backend
python scripts/verify_frontend_import.py
```

---

## 🔧 Maintenance 目录（数据库维护）

维护脚本用于修复数据库结构问题或更新schema。

### add_audit_permission.py
添加审计日志相关权限到系统

```bash
python scripts/maintenance/add_audit_permission.py
```

### add_soft_delete_columns.py
为表添加软删除字段（is_deleted, deleted_at）

```bash
python scripts/maintenance/add_soft_delete_columns.py
```

### fix_audit_log_table.py
修复audit_log表结构问题

```bash
python scripts/maintenance/fix_audit_log_table.py
```

### fix_detail_column.py
修复detail字段类型问题

```bash
python scripts/maintenance/fix_detail_column.py
```

### fix_resource_column.py
修复resource字段长度限制

```bash
python scripts/maintenance/fix_resource_column.py
```

### mark_migration_done.py
标记某个迁移为已完成（修复迁移状态）

```bash
python scripts/maintenance/mark_migration_done.py
```

---

## 🧪 Testing 目录（测试脚本）

测试脚本用于验证系统功能和数据完整性。

### check_audit_data.py
检查审计日志数据

```bash
python scripts/testing/check_audit_data.py
```

### check_audit_table.py
检查audit_log表结构

```bash
python scripts/testing/check_audit_table.py
```

### check_users.py
检查用户数据和密码状态

```bash
python scripts/testing/check_users.py
```

### test_password.py
测试密码验证功能

```bash
python scripts/testing/test_password.py
```

### simple_password_test.py
简单的密码验证测试（使用psycopg2直接连接）

```bash
python scripts/testing/simple_password_test.py
```

---

## ⚠️ 注意事项

### 环境要求
- Python 3.11+
- 已配置 .env 文件
- 数据库服务已启动

### 执行前检查
```bash
# 1. 激活虚拟环境
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 确认数据库连接
# 检查 .env 文件中的 DATABASE_URL

# 3. 检查迁移状态
alembic current
```

### 安全建议
- 🔒 生产环境慎用测试脚本
- 🔒 运行维护脚本前先备份数据库
- 🔒 检查脚本源码，理解其功能后再执行

---

## 📝 开发指南

### 添加新脚本
1. 确定脚本类型（核心/维护/测试）
2. 放入对应目录
3. 添加完整的文档字符串
4. 更新本 README 文档

### 脚本模板
```python
"""
脚本名称：[功能简述]

用途：
[详细说明脚本的用途]

使用方法：
python scripts/[目录]/[脚本名].py

注意事项：
- [重要提示1]
- [重要提示2]
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# 导入所需模块
from app.core.database import AsyncSessionLocal

async def main():
    """主函数"""
    async with AsyncSessionLocal() as session:
        # 实现功能
        pass

if __name__ == "__main__":
    asyncio.run(main())
```

---

**最后更新**: 2026-02-10  
**维护人**: GitHub Copilot  
**新增**: 完整的测试数据生成功能（50,000+订单，72个真实菜品）
