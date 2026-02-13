# 后端依赖说明

本文档说明 backend 目录的 Python 依赖文件用途与维护方式。

## 1. 依赖文件

- `backend/requirements.txt`：运行时依赖（生产）
- `backend/requirements_dev.txt`：开发依赖（测试、检查、格式化）

建议：

- 生产环境优先安装 `requirements.txt`
- 本地开发安装 `requirements_dev.txt`

## 2. 安装方式

```bash
cd backend
pip install -r requirements_dev.txt
```

仅生产依赖：

```bash
pip install -r requirements.txt
```

## 3. 主要依赖分组

### Web 与 API

- fastapi
- uvicorn
- pydantic
- pydantic-settings

### 数据库

- sqlalchemy
- alembic
- asyncpg
- psycopg2-binary（部分同步场景与工具链）

### 安全认证

- python-jose[cryptography]
- passlib[bcrypt]
- bcrypt

### 数据处理

- pandas
- openpyxl

### 测试与质量（dev）

- pytest / pytest-asyncio / pytest-cov
- ruff
- mypy

## 4. 代码规范工具对齐

当前项目后端主要使用：

- ruff（lint + format）
- mypy（类型检查）
- pytest（测试）

建议优先使用 `python dev.py all` 作为提交前检查入口。

## 5. 升级策略

- 优先小版本升级，先在开发环境验证
- 涉及 FastAPI、SQLAlchemy、Pydantic 主版本升级时，必须执行完整回归
- 升级后同步更新相关文档和 CI 配置

## 6. 常见问题

### 安装失败

```bash
python -m pip install --upgrade pip
pip install -r requirements_dev.txt
```

### 版本冲突

- 先确认是否混用了全局 Python 与虚拟环境
- 删除虚拟环境后重建再安装

### 运行时报模块缺失

- 检查当前终端是否已激活 backend 的虚拟环境
- 重新安装依赖并复测
