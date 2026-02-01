# 餐饮企业财务分析与可视化系统

## 项目概述

基于 FastAPI + Vue3 的餐饮企业财务分析与可视化系统，提供完整的财务数据管理、分析和可视化功能。

## 技术栈

### 后端
- **框架**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **数据库迁移**: Alembic
- **数据验证**: Pydantic v2
- **认证**: JWT
- **权限**: RBAC
- **数据库**: PostgreSQL

### 前端
- **框架**: Vue3 + TypeScript
- **构建工具**: Vite
- **UI 框架**: Element Plus
- **图表库**: ECharts
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP 客户端**: Axios

## 项目结构

```
financial_analysis_system/
├── backend/              # 后端服务（FastAPI + SQLAlchemy 2.0）
│   ├── app/             # 应用源代码
│   │   ├── api/         # API 路由和端点（v1版本）
│   │   ├── core/        # 核心配置（数据库、安全、异常）
│   │   ├── models/      # 数据模型（ORM - SQLAlchemy 2.0）
│   │   ├── schemas/     # Pydantic 数据验证模式
│   │   └── services/    # 业务逻辑服务（审计、KPI计算）
│   ├── alembic/         # 数据库迁移脚本（Alembic）
│   ├── scripts/         # 维护和测试脚本
│   │   ├── maintenance/ # 数据库维护（备份、清理）
│   │   ├── testing/     # 测试验证脚本
│   │   ├── seed_data.py # 初始化数据
│   │   ├── export_api_docs.py # 导出 OpenAPI 文档 ⭐
│   │   └── README.md    # 脚本使用文档
│   ├── tests/           # 后端测试文件（pytest）
│   ├── dev.py           # 开发辅助脚本
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端应用（Vue3 + TypeScript + Vite）
│   ├── src/
│   │   ├── api/         # API 客户端封装
│   │   ├── components/  # Vue 组件
│   │   ├── config/      # 配置管理（常量、环境变量）
│   │   ├── router/      # Vue Router 路由配置
│   │   ├── stores/      # Pinia 状态管理
│   │   ├── types/       # TypeScript 类型定义（模块化）
│   │   ├── utils/       # 工具函数（格式化、验证等）
│   │   └── views/       # 页面视图组件
│   ├── public/          # 静态资源
│   └── package.json     # 前端依赖
├── docs/                # 项目文档 📚
│   ├── README.md                     # 📑 文档索引（L0/L1/L2分层说明）⭐
│   ├── development_guide.md          # 🚀 开发指南（环境配置、启动、测试、部署）⭐
│   ├── backend_structure.md          # 🏗️ 后端架构（Clean Architecture 分层设计）⭐
│   ├── frontend_structure.md         # 🎨 前端架构（Vue3 组件、路由、状态管理）⭐
│   ├── naming_conventions.md         # 📐 命名规范（前后端统一风格）⭐
│   ├── project_history.md            # 📖 项目历程（Stage 2-11 开发总结）⭐
│   ├── reports/                      # 📊 历史报告（18个优化分析） → 参见 reports/INDEX.md
│   └── archive/                      # 📦 历史交付（25个阶段文档） → 参见 archive/INDEX.md
├── scripts/             # 工具脚本
│   ├── start.bat        # Windows 启动脚本
│   ├── start.sh         # Linux/Mac 启动脚本
│   └── verify_system.py # 系统验证脚本
└── README.md            # 项目总览（本文件）
```

## 快速开始

### 🚀 推荐方式（统一命令）

#### Windows 环境
```bash
# 1. 首次运行（完整初始化）
scripts\start.bat              # 自动检查环境、创建虚拟环境、安装依赖

# 2. 日常开发（使用统一入口）
dev.bat dev-backend            # 启动后端服务器（http://localhost:8000）
dev.bat dev-frontend           # 启动前端服务器（http://localhost:5173）

# 3. 其他常用命令
dev.bat test-backend           # 运行后端测试
dev.bat lint-backend           # 检查后端代码
dev.bat check-backend          # 运行所有检查（lint+format+type+test）
dev.bat help                   # 查看所有可用命令
```

#### Linux/Mac 环境
```bash
# 1. 首次运行（完整初始化）
scripts/start.sh               # 自动检查环境、创建虚拟环境、安装依赖

# 2. 日常开发（使用Makefile）
make dev-backend               # 启动后端服务器（http://localhost:8000）
make dev-frontend              # 启动前端服务器（http://localhost:5173）

# 3. 其他常用命令
make test-backend              # 运行后端测试
make lint-backend              # 检查后端代码
make check-backend             # 运行所有检查（lint+format+type+test）
make help                      # 查看所有可用命令
```

---

### 📝 传统方式（手动配置）

如果需要手动配置环境，可使用以下步骤：

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 配置 .env 文件中的数据库连接信息
alembic upgrade head
uvicorn app.main:app --reload
```

后端服务将在 http://localhost:8000 启动

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端应用将在 http://localhost:5173 启动

### 一键启动（推荐）

使用项目提供的启动脚本可以同时启动前后端：

**Windows:**
```bash
scripts\start.bat
```

**Linux/Mac:**
```bash
bash scripts/start.sh
```

## 核心功能

### 1. 用户认证与权限管理 🔐
- JWT 令牌认证（access_token + refresh_token）
- 基于角色的访问控制（RBAC）
- 28+ 细粒度权限（user:view, store:create, kpi:export等）
- 完整的用户操作审计日志
- 三种预定义角色（管理员、经理、收银员）

### 2. 门店管理 🏪
- 门店信息CRUD（增删改查）
- 产品分类与产品管理
- 软删除机制
- 按门店查看订单和KPI

### 3. 订单管理 📦
- 订单头和订单项完整管理
- 订单状态流转
- 订单统计分析（按门店、时间）
- 客单价、订单数等关键指标

### 4. 费用管理 💰
- 费用类型自定义配置
- 费用记录批量导入导出
- 多维度费用统计（按类型、门店、时间）
- 月度/季度/年度对比分析

### 5. KPI 数据管理 📊
- 每日KPI数据采集
- 多维度统计（销售、成本、利润、效率）
- 趋势分析（同比、环比）
- KPI数据导出（Excel）

### 6. 审计日志 📝
- 自动记录所有关键操作
- 用户登录/登出追踪
- 数据变更详细记录
- IP地址和时间戳记录

### 7. 数据可视化 📈
- ECharts 图表集成
- 销售趋势图表
- 费用分析图表
- KPI仪表盘
- 多维度数据对比

### 8. 数据导入中心 📥
- CSV批量导入（门店、订单、费用）
- 实时进度跟踪
- 详细错误记录和报告
- 支持增量和全量导入

### 9. 报表中心 📊
- 日汇总报表（销售、订单、费用）
- 月汇总报表（同比、环比）
- 门店绩效报表（排名、对比）
- 费用明细报表（占比分析）
- Excel一键导出

### 10. 门店级数据权限 🔐
- 细粒度数据访问控制
- 用户只能查看授权门店数据
- 结合RBAC的多层权限体系
- 多租户数据隔离

## API 文档

启动后端服务后访问：http://localhost:8000/docs

## 系统验证

项目提供了自动化验证脚本，用于检查系统完整性：

```bash
python scripts/verify_system.py
```

该脚本会执行 57 项检查，包括：
- 📁 文件系统结构（8 项）
- 📄 后端关键文件（10 项）
- 📄 前端关键文件（10 项）
- 🎯 Stage 6 KPI 端点（4 项）
- 📦 类型定义模块化（5 项）
- 🧩 组件结构（3 项）
- ⚙️ 配置文件（5 项）
- 📚 文档完整性（7 项）
- ✨ 代码质量（5 项）

## 文档索引

> 📚 **完整文档体系**: 参见 [docs/README.md](docs/README.md) 了解 L0/L1/L2 三级分层维护规则

### 🚀 快速开始
- **环境配置与启动** → [development_guide.md](docs/development_guide.md)
  - Python 3.11+ / Node.js 18+ / PostgreSQL 14+
  - 数据库迁移（Alembic）
  - 前后端启动脚本

### 🏗️ 架构设计
- **后端架构** → [backend_structure.md](docs/backend_structure.md)
  - Clean Architecture 三层分层（API → Service → Model）
  - 9个核心数据模型（User, Store, Order, KPI等）
  - 异步数据库操作（SQLAlchemy 2.0）
  
- **前端架构** → [frontend_structure.md](docs/frontend_structure.md)
  - Vue3 + TypeScript 组件结构
  - 路由守卫与权限控制（RBAC + 数据权限）
  - Pinia 状态管理模式

### 📐 开发规范
- **命名规范** → [naming_conventions.md](docs/naming_conventions.md)
  - 前后端统一命名风格
  - API 路由命名约定
  - 数据库表名和字段名规范

### 📖 项目历程
- **开发历程** → [project_history.md](docs/project_history.md)
  - Stage 2-11 完整开发记录
  - 10个核心功能实现要点
  - 技术选型和架构演进

### 📊 历史归档
- **优化报告** → [docs/reports/INDEX.md](docs/reports/INDEX.md)
  - 结构优化系列（4份报告）
  - 仓库清理系列（4份报告）
  - 一致性审计系列（3份报告）
  - 按主题分类和时间线可追溯
  
- **阶段交付** → [docs/archive/INDEX.md](docs/archive/INDEX.md)
  - Stage 2-11 阶段交付文档（25个）
  - 按功能模块分类导航
  - 技术决策历史追溯

## 项目状态

✅ **当前版本**: v1.1.0-production-ready  
✅ **系统状态**: 🟢 生产就绪  
✅ **测试通过率**: 100% (57/57)  
✅ **代码质量**: ⭐⭐⭐⭐⭐ 优秀  
✅ **功能完成度**: Stage 2-11 全部完成

---

**最后更新**: 2026年1月27日  
**文档治理**: L0/L1/L2 三级分层维护机制已建立