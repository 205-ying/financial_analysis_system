# Python依赖包说明文档

## 📦 依赖文件说明

### 1. requirements.txt（生产环境）
生产环境必需的核心依赖，仅包含运行应用所需的包。

**安装方式：**
```bash
pip install -r requirements.txt
```

### 2. requirements_dev.txt（开发环境）
开发环境完整依赖，包含测试、代码质量工具等。

**安装方式：**
```bash
pip install -r requirements_dev.txt
```

### 3. requirements_new.txt（pip freeze结果）
当前虚拟环境所有已安装包的快照，用于版本锁定和故障排查。

---

## 📚 核心依赖说明

### FastAPI 生态
| 包名 | 版本 | 用途 |
|------|------|------|
| `fastapi` | 0.104.1 | Web框架核心 |
| `uvicorn[standard]` | 0.24.0 | ASGI服务器 |
| `starlette` | 0.27.0 | FastAPI基础框架 |
| `pydantic` | 2.5.0 | 数据验证 |
| `pydantic-settings` | 2.1.0 | 配置管理 |

### 数据库相关
| 包名 | 版本 | 用途 |
|------|------|------|
| `sqlalchemy` | 2.0.23 | ORM框架 |
| `alembic` | 1.13.0 | 数据库迁移 |
| `asyncpg` | 0.29.0 | PostgreSQL异步驱动 |
| `psycopg2-binary` | 2.9.11 | PostgreSQL同步驱动（备用） |

### 认证与安全
| 包名 | 版本 | 用途 |
|------|------|------|
| `python-jose[cryptography]` | 3.3.0 | JWT令牌处理 |
| `passlib[bcrypt]` | 1.7.4 | 密码哈希（包装器） |
| `bcrypt` | 5.0.0 | 密码加密算法 |
| `cryptography` | 46.0.3 | 加密库 |
| `python-multipart` | 0.0.6 | 文件上传支持 |

### 日志与工具
| 包名 | 版本 | 用途 |
|------|------|------|
| `loguru` | 0.7.2 | 结构化日志 |
| `python-dateutil` | 2.8.2 | 日期时间处理 |
| `python-dotenv` | 1.2.1 | 环境变量加载 |

### HTTP客户端
| 包名 | 版本 | 用途 |
|------|------|------|
| `httpx` | 0.25.2 | 异步HTTP客户端 |
| `requests` | 2.32.5 | 同步HTTP客户端 |
| `aiohttp` | 3.13.3 | 异步HTTP框架 |

### 可选依赖
| 包名 | 版本 | 用途 |
|------|------|------|
| `redis` | 5.0.1 | 缓存支持（未来使用） |

---

## 🛠️ 开发工具说明

### 测试框架
| 包名 | 版本 | 用途 |
|------|------|------|
| `pytest` | 7.4.3 | 单元测试框架 |
| `pytest-asyncio` | 0.21.1 | 异步测试支持 |
| `pytest-cov` | 4.1.0 | 代码覆盖率 |
| `coverage` | 7.13.1 | 覆盖率报告 |

### 代码质量
| 包名 | 版本 | 用途 |
|------|------|------|
| `black` | 23.11.0 | 代码格式化（PEP 8） |
| `flake8` | 6.1.0 | 代码风格检查 |
| `isort` | 5.12.0 | import排序 |
| `mypy` | 1.7.1 | 静态类型检查 |
| `pre-commit` | 3.5.0 | Git提交前检查 |

### 数据生成
| 包名 | 版本 | 用途 |
|------|------|------|
| `factory_boy` | 3.3.1 | 测试数据工厂 |
| `Faker` | 20.1.0 | 假数据生成 |

---

## 📝 使用场景

### 场景1：生产部署
```bash
# 仅安装生产依赖
pip install -r requirements.txt
```

### 场景2：本地开发
```bash
# 安装完整开发环境
pip install -r requirements_dev.txt
```

### 场景3：版本锁定
```bash
# 导出当前环境所有包
pip freeze > requirements_new.txt
```

### 场景4：依赖更新
```bash
# 更新某个包
pip install --upgrade fastapi

# 重新生成锁定文件
pip freeze > requirements_new.txt
```

---

## 🔍 代码中的实际使用

### 1. FastAPI核心
```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
```

### 2. 数据库操作
```python
# app/core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import MetaData

# app/models/user.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
```

### 3. 数据验证
```python
# app/schemas/store.py
from pydantic import BaseModel, Field
```

### 4. 认证安全
```python
# app/core/security.py
import bcrypt
from jose import JWTError, jwt
```

### 5. 日志记录
```python
# app/main.py
from loguru import logger
```

---

## ⚠️ 重要注意事项

### 1. bcrypt独立安装
虽然`passlib[bcrypt]`会自动安装bcrypt，但我们显式声明`bcrypt==5.0.0`以确保版本一致：
```python
# app/core/security.py 和 scripts/seed_data.py 直接使用
import bcrypt
```

### 2. psycopg2-binary
用于同步连接（主要在alembic迁移中）：
```ini
# alembic.ini
sqlalchemy.url = postgresql://user:pass@host/db
```

### 3. 开发工具可选
`requirements.txt`中开发工具被注释，避免生产环境安装不必要的包。

### 4. Python版本要求
```toml
# pyproject.toml
requires-python = ">=3.11"
```
确保使用Python 3.11+以支持所有类型注解特性。

---

## 🔄 依赖更新策略

### 安全更新（推荐定期执行）
```bash
# 检查过期包
pip list --outdated

# 更新安全补丁版本
pip install --upgrade sqlalchemy psycopg2-binary cryptography
```

### 主版本升级（需谨慎测试）
- FastAPI: 0.104.x → 0.110.x（需测试API兼容性）
- SQLAlchemy: 2.0.x → 2.1.x（需测试ORM变化）
- Pydantic: 2.5.x → 2.9.x（需测试验证逻辑）

---

## 📊 依赖关系图

```
fastapi (0.104.1)
├── starlette (0.27.0)
│   ├── anyio (3.7.1)
│   └── typing-extensions (4.15.0)
├── pydantic (2.5.0)
│   └── pydantic-core (2.14.1)
└── uvicorn[standard] (0.24.0)
    ├── h11 (0.16.0)
    ├── httptools (0.7.1)
    └── watchfiles (1.1.1)

sqlalchemy (2.0.23)
├── greenlet (3.3.0)
└── typing-extensions (4.15.0)

alembic (1.13.0)
├── Mako (1.3.10)
└── sqlalchemy (2.0.23)

python-jose[cryptography] (3.3.0)
├── ecdsa (0.19.1)
├── pyasn1 (0.6.2)
├── rsa (4.9.1)
└── cryptography (46.0.3)

passlib[bcrypt] (1.7.4)
└── bcrypt (5.0.0)
```

---

## 📞 问题排查

### 问题1：ModuleNotFoundError
```bash
# 确认虚拟环境已激活
.\venv\Scripts\Activate.ps1  # Windows PowerShell
source venv/bin/activate      # Linux/Mac

# 重新安装依赖
pip install -r requirements.txt
```

### 问题2：版本冲突
```bash
# 清理环境重新安装
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### 问题3：安装失败
```bash
# 检查pip版本
pip --version
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## ✅ 检查清单

- [ ] requirements.txt 包含所有生产依赖
- [ ] requirements_dev.txt 包含开发工具
- [ ] 所有依赖已在代码中实际使用
- [ ] 版本号与虚拟环境一致
- [ ] pyproject.toml 配置正确
- [ ] 文档说明完整

---

**更新日期：** 2026-01-23  
**维护者：** 开发团队
