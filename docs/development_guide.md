# 开发指南

## 统一命令表（推荐入口）

### Windows 环境（推荐）

使用 `dev.bat` 作为主入口，提供所有常用开发命令：

| 命令 | 功能 | 说明 |
|-----|------|------|
| `dev.bat help` | 显示帮助 | 查看所有可用命令 |
| `dev.bat install` | 安装所有依赖 | 首次运行必需（前后端） |
| `dev.bat install-backend` | 安装后端依赖 | 仅安装Python依赖 |
| `dev.bat install-frontend` | 安装前端依赖 | 仅安装npm依赖 |
| `dev.bat dev-backend` | 启动后端服务器 | http://localhost:8000 |
| `dev.bat dev-frontend` | 启动前端服务器 | http://localhost:5173 |
| `dev.bat test` | 运行所有测试 | 前后端测试 |
| `dev.bat test-backend` | 运行后端测试 | pytest + 覆盖率 |
| `dev.bat lint` | 检查所有代码 | 前后端代码检查 |
| `dev.bat lint-backend` | 检查后端代码 | ruff检查 |
| `dev.bat lint-frontend` | 检查前端代码 | ESLint检查 |
| `dev.bat format` | 格式化所有代码 | 前后端代码格式化 |
| `dev.bat format-backend` | 格式化后端代码 | ruff格式化 |
| `dev.bat format-frontend` | 格式化前端代码 | Prettier格式化 |
| `dev.bat check` | 运行所有检查 | lint+format+type+test |
| `dev.bat check-backend` | 运行后端所有检查 | lint+format+type+test |
| `dev.bat check-frontend` | 运行前端所有检查 | lint+format+type+test |
| `dev.bat migrate` | 数据库迁移 | alembic upgrade head |
| `dev.bat clean` | 清理生成文件 | 删除缓存和临时文件 |

### 跨平台环境（Linux/Mac/CI）

使用 `Makefile`（命令与 dev.bat 完全对应）：

```bash
make help               # 显示帮助
make install            # 安装所有依赖
make install-backend    # 安装后端依赖
make install-frontend   # 安装前端依赖
make dev-backend        # 启动后端服务器
make dev-frontend       # 启动前端服务器
make test               # 运行所有测试
make test-backend       # 运行后端测试
make lint               # 检查所有代码
make lint-backend       # 检查后端代码
make lint-frontend      # 检查前端代码
make format             # 格式化所有代码
make format-backend     # 格式化后端代码
make format-frontend    # 格式化前端代码
make check              # 运行所有检查
make check-backend      # 运行后端所有检查
make check-frontend     # 运行前端所有检查
make migrate            # 数据库迁移
make clean              # 清理生成文件
```

### 其他脚本（特定场景）

#### 快捷启动（已配置环境）
```bash
cd backend
start_dev.bat           # Windows CMD
start_dev.ps1           # PowerShell
python dev.py start     # Python直接调用
```

⚠️ **注意**: 假设环境已配置（虚拟环境、依赖、.env），不进行环境检查。适用于快速重启服务。

#### 首次运行（完整初始化）
```bash
scripts\start.bat       # Windows 首次部署
scripts/start.sh        # Linux/Mac 首次部署
```

✅ **包含**: 环境检查 → 创建虚拟环境 → 安装依赖 → 复制.env → 迁移数据库 → 启动服务

#### 系统验证（CI/CD）
```bash
python scripts/verify_system.py
```

✅ **用途**: 检查文件结构完整性，验证所有关键文件是否存在。

---

## 项目架构概览

### 整体架构

本项目采用**前后端分离**架构，后端提供 RESTful API 服务，前端为 SPA (Single Page Application)。

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│   Vue3 前端     │ ◄─────────────► │   FastAPI 后端  │
│   (Port 5173)   │                 │   (Port 8000)   │
└─────────────────┘                 └─────────────────┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │   PostgreSQL    │
                                    │   数据库        │
                                    └─────────────────┘
```

### 后端架构 (Clean Architecture)

```
┌─────────────────────────────────────────────────────┐
│                   API Layer                         │
│  FastAPI Routes, Middleware, Exception Handlers    │
├─────────────────────────────────────────────────────┤
│                 Service Layer                       │
│     Business Logic, Use Cases, Validations         │
├─────────────────────────────────────────────────────┤
│                Repository Layer                     │
│    Data Access, Query Building, ORM Operations     │
├─────────────────────────────────────────────────────┤
│                 Model Layer                         │
│      Database Models, Domain Entities              │
└─────────────────────────────────────────────────────┘
```

### 前端架构 (Vue3 + TypeScript)

```
┌─────────────────────────────────────────────────────┐
│                 View Layer                          │
│        Vue Components, Pages, Layouts              │
├─────────────────────────────────────────────────────┤
│               Store Layer (Pinia)                   │
│       State Management, Actions, Getters           │
├─────────────────────────────────────────────────────┤
│               Service Layer                         │
│         HTTP Client, API Calls, Utils              │
├─────────────────────────────────────────────────────┤
│               Router Layer                          │
│     Navigation, Guards, Route Management           │
└─────────────────────────────────────────────────────┘
```

## 数据模型设计

### 核心实体关系

```mermaid
erDiagram
    USER ||--o{ AUDIT_LOG : creates
    USER }o--|| ROLE : has
    ROLE ||--o{ ROLE_PERMISSION : contains
    PERMISSION ||--o{ ROLE_PERMISSION : granted
    
    STORE ||--o{ ORDER : generates
    STORE ||--o{ EXPENSE_DETAIL : incurs
    STORE ||--o{ KPI_DAILY : measured
    
    ORDER ||--o{ ORDER_DETAIL : contains
    
    EXPENSE_CATEGORY ||--o{ EXPENSE_DETAIL : categorizes
    
    USER {
        int id PK
        string username
        string email
        string password_hash
        boolean is_active
        datetime created_at
    }
    
    ROLE {
        int id PK
        string name
        string description
        datetime created_at
    }
    
    PERMISSION {
        int id PK
        string name
        string resource
        string action
        string description
    }
    
    STORE {
        int id PK
        string name
        string address
        string phone
        boolean is_active
        datetime created_at
    }
    
    ORDER {
        int id PK
        int store_id FK
        string order_no
        decimal total_amount
        datetime order_time
        string status
    }
    
    ORDER_DETAIL {
        int id PK
        int order_id FK
        string item_name
        int quantity
        decimal unit_price
        decimal amount
    }
    
    EXPENSE_CATEGORY {
        int id PK
        string name
        string code
        boolean is_active
    }
    
    EXPENSE_DETAIL {
        int id PK
        int store_id FK
        int category_id FK
        decimal amount
        string description
        date expense_date
    }
    
    KPI_DAILY {
        int id PK
        int store_id FK
        date business_date
        decimal revenue
        decimal cost
        decimal profit
        int order_count
    }
    
    AUDIT_LOG {
        int id PK
        int user_id FK
        string action
        string resource
        string details
        datetime created_at
    }
```

### 数据域说明

#### 1. 用户权限域
- **用户 (User)**: 系统使用者
- **角色 (Role)**: 用户角色定义
- **权限 (Permission)**: 具体权限项
- **审计日志 (AuditLog)**: 操作记录

#### 2. 门店业务域
- **门店 (Store)**: 餐饮门店信息
- **订单 (Order)**: 门店订单主表
- **订单明细 (OrderDetail)**: 订单详细信息

#### 3. 费用管理域
- **费用科目 (ExpenseCategory)**: 费用分类
- **费用明细 (ExpenseDetail)**: 具体费用记录

#### 4. 数据分析域
- **日指标汇总 (KpiDaily)**: 门店日度 KPI 数据

## 权限设计

### RBAC 模型

```
User ←→ Role ←→ Permission
```

### 权限粒度

1. **菜单权限**: 控制页面访问
2. **接口权限**: 控制 API 调用
3. **数据权限**: 控制数据访问范围
4. **操作权限**: 控制具体操作（增删改查）

### 预定义角色

- **超级管理员**: 所有权限
- **系统管理员**: 系统管理权限
- **门店管理员**: 门店数据管理
- **财务人员**: 财务数据查看和分析
- **普通用户**: 基本查看权限

## 技术约定

### 代码规范

#### 后端 (Python)
- 使用 **Black** 进行代码格式化
- 使用 **isort** 进行导入排序
- 使用 **flake8** 进行语法检查
- 使用 **mypy** 进行类型检查
- 函数名使用 `snake_case`
- 类名使用 `PascalCase`
- 常量使用 `UPPER_SNAKE_CASE`

#### 前端 (TypeScript)
- 使用 **ESLint** + **Prettier** 进行代码规范
- 使用 **Stylelint** 进行样式检查
- 组件名使用 `PascalCase`
- 文件名使用 `kebab-case`
- 变量名使用 `camelCase`
- 常量使用 `UPPER_SNAKE_CASE`

### Git 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**类型说明**:
- `feat`: 新功能
- `fix`: 错误修复
- `docs`: 文档更改
- `style`: 代码格式修改
- `refactor`: 重构代码
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

**示例**:
```
feat(auth): 添加 JWT 认证功能
fix(orders): 修复订单金额计算错误
docs: 更新 API 文档
```

### API 设计规范

#### RESTful API 约定

```
GET    /api/v1/stores          # 获取门店列表
GET    /api/v1/stores/{id}     # 获取门店详情
POST   /api/v1/stores          # 创建门店
PUT    /api/v1/stores/{id}     # 更新门店
DELETE /api/v1/stores/{id}     # 删除门店
```

#### 统一响应格式

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    // 响应数据
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 分页响应格式

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20,
    "has_next": true
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## 开发环境搭建

### 环境要求

- **Python**: 3.11+
- **Node.js**: 18+
- **PostgreSQL**: 14+
- **Redis**: 6+ (可选，用于缓存和会话)

### 快速启动

1. **克隆项目**
```bash
git clone <repository-url>
cd financial_analysis_system
```

2. **启动服务**
```bash
# Windows
scripts\start.bat

# Linux/macOS
chmod +x scripts/start.sh
./scripts/start.sh
```

3. **访问应用**
- 前端: http://localhost:5173
- 后端: http://localhost:8000
- API 文档: http://localhost:8000/docs

### 手动启动

#### 后端启动

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动服务 (注意：使用 app.main:app 而不是 src.app.main:app)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.development
# 编辑 .env.development 文件

# 启动开发服务器
npm run dev
```

## 测试策略

### 后端测试

- **单元测试**: 测试单个函数或方法
- **集成测试**: 测试模块间交互
- **API 测试**: 测试 HTTP 接口

```bash
cd backend

# 运行所有测试
pytest

# 运行指定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=src --cov-report=html
```

### 前端测试

- **单元测试**: 组件和工具函数测试
- **E2E 测试**: 端到端功能测试

```bash
cd frontend

# 运行单元测试
npm run test

# 运行覆盖率测试
npm run test:coverage
```

## 部署指南

### 生产环境构建

#### 后端构建

```bash
cd backend

# 安装生产依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 使用 Gunicorn 启动（生产环境推荐）
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 前端构建

```bash
cd frontend

# 构建生产版本
npm run build

# 构建结果在 dist/ 目录
```

### 环境配置

#### 生产环境变量

**后端 (.env)**:
```env
ENV=production
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=your-production-secret-key
REDIS_URL=redis://localhost:6379/0
```

**前端 (.env.production)**:
```env
VITE_APP_ENV=production
VITE_APP_BASE_API=https://your-api-domain.com/api/v1
```

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查 PostgreSQL 服务是否启动
   - 验证数据库连接字符串
   - 确认数据库用户权限

2. **前端页面空白**
   - 检查控制台错误信息
   - 验证 API 基础地址配置
   - 确认后端服务是否正常运行

3. **API 请求 CORS 错误**
   - 检查后端 CORS 配置
   - 验证前端请求地址

4. **认证问题**
   - 检查 JWT 密钥配置
   - 验证 token 过期时间
   - 确认权限配置正确

### 日志查看

#### 后端日志

日志文件位置: `backend/logs/`

```bash
# 查看实时日志
tail -f backend/logs/app.log
```

#### 前端日志

开发模式下在浏览器控制台查看。

### 性能监控

- 后端: 使用 FastAPI 内置的性能监控
- 前端: 使用浏览器开发者工具
- 数据库: PostgreSQL 慢查询日志

## 前端自动生成文件管理

### 生成文件策略

项目采用 **不提交策略（Git Ignore）** 管理自动生成的类型声明文件：

#### auto-imports.d.ts
- **生成工具**: `unplugin-auto-import` 
- **用途**: 自动导入 Vue、Vue Router、Pinia、VueUse 等常用 API
- **配置位置**: [frontend/vite.config.ts](../frontend/vite.config.ts)
- **Git 策略**: ❌ 不提交（已在 `.gitignore` 忽略）
- **生成时机**: 运行 `npm run dev` 或 `npm run build` 时自动生成
- **可再生性**: ✅ 完全可再生，每次构建自动更新

#### components.d.ts
- **生成工具**: `unplugin-vue-components`
- **用途**: 自动导入 Element Plus 组件和项目组件，提供类型提示
- **配置位置**: [frontend/vite.config.ts](../frontend/vite.config.ts)
- **Git 策略**: ❌ 不提交（已在 `.gitignore` 忽略）
- **生成时机**: 运行 `npm run dev` 或 `npm run build` 时自动生成
- **可再生性**: ✅ 完全可再生，根据组件使用情况自动更新

### CI/CD 配置要求

```yaml
# 示例: .github/workflows/frontend.yml
- name: Install dependencies
  run: cd frontend && npm install
  # ↑ npm install 会触发 postinstall 钩子，生成类型文件

- name: Type check
  run: cd frontend && npm run type-check
  # ↑ 此时 auto-imports.d.ts 和 components.d.ts 已存在

- name: Build
  run: cd frontend && npm run build
```

**重要提示**:
- 🚫 **禁止手动编辑** 这两个文件，所有修改会在下次构建时被覆盖
- ✅ CI/CD 环境只需运行 `npm install`，插件会自动生成所需文件
- ⚠️ 如果遇到类型错误，检查 `vite.config.ts` 中的 AutoImport 和 Components 配置

### barrel exports (index.ts) 使用规范

项目中各模块的 `index.ts` 导出策略：

| 模块 | 是否使用 index.ts | 用途 | 说明 |
|------|------------------|------|------|
| **api/** | ✅ 使用 | 统一API导出 | 所有API模块通过 `@/api` 统一导出（如 `roleApi`, `permissionApi`） |
| **types/** | ✅ 使用 | 统一类型导出 | 核心入口，所有类型从此导出 |
| **stores/** | ✅ 使用 | setupStore + 导出stores | main.ts 需要 setupStore 函数 |
| **directives/** | ✅ 使用 | 导出指令安装函数 | main.ts 需要 setupPermissionDirective |
| **components/** | ✅ 使用 | 导出公共组件 | FilterBar 等公共组件统一导出 |
| **config/** | ✅ 使用 | 导出配置常量 | 环境变量、常量统一管理 |
| **router/** | ✅ 使用 | 标准路由入口 | Vue Router 标准结构 |

**导入示例**:
```typescript
// ✅ 推荐 - 使用 index.ts 的模块
import { LoginRequest, UserInfo } from '@/types'
import { setupStore } from '@/stores'
import { setupPermissionDirective } from '@/directives'
import { FilterBar } from '@/components'
import { STORAGE_KEYS } from '@/config'

// ✅ 推荐 - API 通过统一入口导入
import { roleApi, permissionApi } from '@/api'
import { login, logout } from '@/api/auth'
import { getOrderList } from '@/api/order'
import { getKPISummary } from '@/api/kpi'

// ✅ 也可以直接按模块导入
import { roleApi as roleApiModule } from '@/api/role'
```

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Vue3 官方文档](https://vuejs.org/)
- [SQLAlchemy 官方文档](https://docs.sqlalchemy.org/)
- [Element Plus 文档](https://element-plus.org/)
- [ECharts 文档](https://echarts.apache.org/)