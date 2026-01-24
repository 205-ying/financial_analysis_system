# Backend 重构指南

## 目标结构

```
backend/
├── app/                          # 应用主目录 (Python包)
│   ├── __init__.py
│   ├── main.py                  # FastAPI应用入口
│   │
│   ├── api/                     # API路由层
│   │   ├── __init__.py
│   │   ├── deps.py              # 依赖注入 (数据库会话、当前用户等)
│   │   ├── router.py            # 路由汇总
│   │   └── v1/                  # API v1版本
│   │       ├── __init__.py
│   │       ├── auth.py          # 认证：登录、注册、获取用户信息
│   │       ├── health.py        # 健康检查
│   │       ├── stores.py        # 门店管理CRUD
│   │       ├── orders.py        # 订单管理CRUD
│   │       ├── kpi.py           # KPI数据查询
│   │       ├── expense_types.py # 费用科目管理
│   │       └── expense_records.py # 费用记录管理
│   │
│   ├── core/                    # 核心配置模块
│   │   ├── __init__.py
│   │   ├── config.py            # 应用配置 (使用pydantic-settings)
│   │   ├── database.py          # 数据库连接和会话管理
│   │   ├── security.py          # JWT认证、密码哈希
│   │   ├── logging.py           # 日志配置
│   │   └── exceptions.py        # 自定义异常和异常处理器
│   │
│   ├── models/                  # SQLAlchemy数据库模型
│   │   ├── __init__.py          # 导出所有模型
│   │   ├── base.py              # 基础Mixin类 (IDMixin, TimestampMixin等)
│   │   ├── user.py              # 用户、角色、权限模型
│   │   ├── store.py             # 门店、产品分类、产品模型
│   │   ├── order.py             # 订单头、订单项模型
│   │   ├── expense.py           # 费用科目、费用记录模型
│   │   └── kpi.py               # KPI日报模型、审计日志模型
│   │
│   ├── schemas/                 # Pydantic数据验证Schema
│   │   ├── __init__.py
│   │   ├── common.py            # 通用Schema (Response, PageData等)
│   │   ├── auth.py              # 认证相关Schema
│   │   ├── store.py             # 门店相关Schema
│   │   ├── order.py             # 订单相关Schema
│   │   ├── expense.py           # 费用相关Schema
│   │   └── kpi.py               # KPI相关Schema
│   │
│   └── services/                # 业务逻辑服务层
│       ├── __init__.py
│       ├── audit.py             # 审计日志服务
│       └── kpi_calculator.py    # KPI计算服务
│
├── alembic/                     # 数据库迁移
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── scripts/                     # 工具脚本
│   ├── seed_data.py            # 数据库种子数据
│   └── verify_constraints.py   # 验证数据库约束
│
├── tests/                       # 测试
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
│
├── logs/                        # 日志输出目录
│
├── .env                         # 环境变量配置
├── .env.example                 # 环境变量示例
├── alembic.ini                  # Alembic配置
├── pyproject.toml               # 项目配置
├── pytest.ini                   # Pytest配置
├── requirements.txt             # 生产环境依赖
├── requirements-dev.txt         # 开发环境依赖
├── start_dev.ps1               # Windows开发环境启动脚本
└── start_dev.bat               # Windows批处理启动脚本
```

## 关键改进

### 1. 简化目录结构
- **移除** `src/` 嵌套，直接使用 `app/` 作为应用根目录
- **原因**：
  - 减少不必要的目录层级
  - scripts/ 和 alembic/ 已经期望 `app.*` 导入路径
  - 符合FastAPI项目最佳实践

### 2. 统一导入路径
- **绝对导入**：所有模块使用 `from app.xxx import yyy`
- **禁止相对导入**：避免 `from .xxx` 或 `from ..xxx`
- **原因**：
  - 导入路径清晰明确
  - 避免相对导入的复杂性和错误
  - 便于IDE智能提示和重构

### 3. 优化模块职责

#### API层 (`app/api/`)
- `deps.py`：集中管理依赖注入函数
- `router.py`：汇总所有v1路由
- `v1/`：具体的API端点实现

#### Core层 (`app/core/`)
- `config.py`：环境变量和配置管理
- `database.py`：数据库引擎和会话
- `security.py`：认证和授权
- `logging.py`：日志配置
- `exceptions.py`：异常定义和处理器

#### Models层 (`app/models/`)
- 数据库表模型
- 使用 SQLAlchemy 2.0+ 异步语法

#### Schemas层 (`app/schemas/`)
- API请求/响应验证
- 使用 Pydantic v2

#### Services层 (`app/services/`)
- 复杂业务逻辑
- 跨模型操作

### 4. 删除冗余文件
- **删除** `src/app/api/v1/expenses.py`
- **保留** `src/app/api/v1/expense_records.py`（功能更完整）
- **删除** 所有 `__pycache__/` 目录

## 实施步骤

### 步骤 1：备份当前代码
```powershell
# 创建备份
cd C:\Users\29624\Desktop\financial_analysis_system
Copy-Item backend backend_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss') -Recurse
```

### 步骤 2：创建新目录结构
```powershell
cd backend

# 创建 app 目录结构
New-Item -ItemType Directory -Path "app" -Force
New-Item -ItemType Directory -Path "app\api\v1" -Force
New-Item -ItemType Directory -Path "app\core" -Force
New-Item -ItemType Directory -Path "app\models" -Force
New-Item -ItemType Directory -Path "app\schemas" -Force
New-Item -ItemType Directory -Path "app\services" -Force

# 创建 __init__.py
New-Item -ItemType File -Path "app\__init__.py" -Force
New-Item -ItemType File -Path "app\api\__init__.py" -Force
New-Item -ItemType File -Path "app\api\v1\__init__.py" -Force
New-Item -ItemType File -Path "app\core\__init__.py" -Force
New-Item -ItemType File -Path "app\models\__init__.py" -Force
New-Item -ItemType File -Path "app\schemas\__init__.py" -Force
New-Item -ItemType File -Path "app\services\__init__.py" -Force
```

### 步骤 3：复制文件
```powershell
# 复制主文件
Copy-Item "src\app\main.py" "app\main.py" -Force

# 复制 core
Copy-Item "src\app\core\*.py" "app\core\" -Force -Exclude "__pycache__"

# 复制 models
Copy-Item "src\app\models\*.py" "app\models\" -Force -Exclude "__pycache__"

# 复制 schemas
Copy-Item "src\app\schemas\*.py" "app\schemas\" -Force -Exclude "__pycache__"

# 复制 services
Copy-Item "src\app\services\*.py" "app\services\" -Force -Exclude "__pycache__"

# 复制 API v1
Copy-Item "src\app\api\v1\*.py" "app\api\v1\" -Force -Exclude "__pycache__", "expenses.py"
```

### 步骤 4：批量更新导入路径（使用Python脚本）
创建 `scripts/update_imports.py`：

```python
"""批量更新导入路径的脚本"""
import os
import re
from pathlib import Path

def update_imports(file_path: Path):
    """更新单个文件的导入路径"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换相对导入为绝对导入
    replacements = [
        # 三级相对导入 (from ...xxx)
        (r'from \.\.\.core\.', 'from app.core.'),
        (r'from \.\.\.models\.', 'from app.models.'),
        (r'from \.\.\.schemas\.', 'from app.schemas.'),
        (r'from \.\.\.services\.', 'from app.services.'),
        (r'from \.\.\.api\.', 'from app.api.'),
        
        # 二级相对导入 (from ..xxx)
        (r'from \.\.core\.', 'from app.core.'),
        (r'from \.\.models\.', 'from app.models.'),
        (r'from \.\.schemas\.', 'from app.schemas.'),
        (r'from \.\.services\.', 'from app.services.'),
        (r'from \.\.api\.', 'from app.api.'),
        
        # 一级相对导入 (from .xxx) - 需要根据上下文处理
        (r'from \.core\.', 'from app.core.'),
        (r'from \.database import', 'from app.core.database import'),
        (r'from \.config import', 'from app.core.config import'),
        (r'from \.security import', 'from app.core.security import'),
        (r'from \.base import', 'from app.models.base import'),
        (r'from \.user import', 'from app.models.user import'),
        (r'from \.common import', 'from app.schemas.common import'),
        (r'from \.auth import', 'from app.schemas.auth import'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """主函数"""
    app_dir = Path('app')
    
    # 递归处理所有Python文件
    for py_file in app_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue
        print(f"Processing: {py_file}")
        update_imports(py_file)
    
    print("\n✅ All imports updated!")

if __name__ == '__main__':
    main()
```

运行脚本：
```powershell
& venv\Scripts\python.exe scripts\update_imports.py
```

### 步骤 5：更新其他文件的导入

#### tests/test_main.py
```python
# 修改
from src.app.main import app
# 为
from app.main import app
```

#### alembic/env.py
```python
# 应该已经使用绝对导入
from app.core.config import settings
from app.core.database import Base
```

#### scripts/seed_data.py
```python
# 应该已经使用绝对导入
from app.core.database import AsyncSessionLocal
from app.models.user import User, Role, Permission
```

### 步骤 6：清理旧结构
```powershell
# 删除 src 目录
Remove-Item "src" -Recurse -Force

# 删除所有 __pycache__
Get-ChildItem -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

### 步骤 7：验证
```powershell
# 语法检查
& venv\Scripts\python.exe -m py_compile app\main.py

# 导入测试
& venv\Scripts\python.exe -c "from app.main import app; print('✅ Import successful!')"

# 启动服务器测试
& venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

## 导入规则参考

### ✅ 正确的导入方式
```python
# app/main.py
from app.core.config import settings
from app.core.database import create_tables
from app.api.router import api_router

# app/api/v1/auth.py
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

# app/models/user.py
from app.core.database import Base
from app.models.base import IDMixin, TimestampMixin

# app/services/audit.py
from app.models.kpi import AuditLog
from app.models.user import User
```

### ❌ 避免的导入方式
```python
# ❌ 相对导入
from .core.config import settings
from ..models.user import User
from ...core.database import get_db

# ❌ src 前缀
from src.app.main import app
from src.app.models.user import User
```

## 注意事项

1. **编码问题**：
   - 所有Python文件使用 UTF-8 编码
   - 避免使用 `-NoNewline` 参数保存文件
   - 使用正确的文本编辑器（VS Code, PyCharm等）

2. **导入顺序**：
   ```python
   # 标准库
   import os
   from typing import Optional
   
   # 第三方库
   from fastapi import FastAPI
   from sqlalchemy import select
   
   # 本地模块
   from app.core.config import settings
   from app.models.user import User
   ```

3. **__init__.py 作用**：
   - 标识目录为Python包
   - 可以导出常用类/函数简化导入
   - models/__init__.py 应导出所有模型

4. **避免循环导入**：
   - 业务逻辑放在 services/
   - 数据模型在 models/
   - API路由在 api/
   - 保持单向依赖：api → services → models

## 测试清单

- [ ] Python模块导入无错误
- [ ] FastAPI应用启动成功
- [ ] 健康检查端点响应正常
- [ ] 数据库连接正常
- [ ] 登录功能正常
- [ ] API文档访问正常 (http://localhost:8000/docs)
- [ ] Alembic迁移正常工作
- [ ] 单元测试通过

## 常见问题

### Q: ModuleNotFoundError: No module named 'app'
**A**: 确保：
1. 当前工作目录是 `backend/`
2. `backend/` 已添加到 Python 路径
3. 运行命令：`python -m uvicorn app.main:app` 而不是 `python app/main.py`

### Q: ImportError: attempted relative import beyond top-level package
**A**: 还有相对导入未替换，检查导入语句是否以 `from app.` 开头

### Q: UnicodeDecodeError
**A**: 文件编码问题，使用UTF-8重新保存文件

## 参考资源

- [FastAPI项目结构](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Python导入系统](https://docs.python.org/3/reference/import.html)
- [SQLAlchemy 2.0文档](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2文档](https://docs.pydantic.dev/latest/)
