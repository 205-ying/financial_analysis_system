# Backend Scripts 说明文档

本目录包含后端维护、测试和数据管理脚本。

---

## 📁 目录结构

```
scripts/
├── seed_data.py                      # 初始化种子数据（核心脚本）⭐
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

### generate_bulk_data.py - 生成批量测试数据
**用途**: 用于性能测试和功能验证

**功能**:
- 生成大量订单数据
- 生成费用记录
- 模拟真实业务场景

**使用方法**:
```bash
cd backend
python scripts/generate_bulk_data.py
```

**配置**:
- 可在脚本中修改生成数据的数量
- 数据时间范围可配置

---

### clean_bulk_data.py - 清理批量测试数据
**用途**: 清理测试数据，恢复干净环境

**功能**:
- 删除测试订单
- 删除测试费用记录
- 保留核心配置数据

**使用方法**:
```bash
cd backend
python scripts/clean_bulk_data.py
```

**安全性**:
- ✅ 只删除测试数据，不影响基础配置
- ✅ 保留用户、门店、产品等核心数据

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

**最后更新**: 2026-01-26  
**维护人**: GitHub Copilot
