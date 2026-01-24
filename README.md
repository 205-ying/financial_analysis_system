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
│   │   ├── api/         # API 路由和端点
│   │   ├── core/        # 核心配置（数据库、安全等）
│   │   ├── models/      # 数据模型（ORM）
│   │   ├── schemas/     # Pydantic 数据验证模式
│   │   └── services/    # 业务逻辑服务
│   ├── alembic/         # 数据库迁移脚本
│   ├── scripts/         # 维护和测试脚本
│   │   ├── maintenance/ # 数据库维护脚本
│   │   ├── testing/     # 测试验证脚本
│   │   └── README.md    # 脚本使用文档
│   ├── tests/           # 后端测试文件
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
├── docs/                # 项目文档
│   ├── README.md                            # 文档索引 📚
│   ├── development_guide.md                 # 开发指南
│   ├── backend_structure.md                 # 后端架构文档
│   ├── frontend_structure.md                # 前端架构文档
│   ├── OPTIMIZATION_HISTORY.md              # 优化历史记录
│   ├── system_verification_report_final.md  # 系统验证报告
│   └── archive/         # 历史文档归档（30+ 文件）
├── scripts/             # 工具脚本
│   ├── start.bat        # Windows 启动脚本
│   ├── start.sh         # Linux/Mac 启动脚本
│   └── verify_system.py # 系统验证脚本
└── README.md            # 项目总览（本文件）
```

## 快速开始

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

- 🏪 门店管理
- 📊 订单分析
- 💰 费用管理
- 📈 财务指标
- 👥 用户权限管理
- 📝 审计日志
- 📊 数据可视化

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

## 开发指南

请参考 [docs/](docs/) 目录下的开发文档：

**核心文档** ⭐
- [docs/README.md](docs/README.md) - 📚 文档索引（查看所有文档）
- [docs/development_guide.md](docs/development_guide.md) - 开发指南
- [docs/backend_structure.md](docs/backend_structure.md) - 后端架构说明
- [docs/frontend_structure.md](docs/frontend_structure.md) - 前端架构说明

**工具文档**
- [backend/scripts/README.md](backend/scripts/README.md) - 后端脚本使用指南
- [docs/optimization_history.md](docs/optimization_history.md) - 项目优化历史
- [docs/project_optimization_report.md](docs/project_optimization_report.md) - 项目优化报告

**验证报告**
- [docs/system_verification_report_final.md](docs/system_verification_report_final.md) - 系统验证报告（57/57 通过）

> 💡 更多历史文档请查看 [docs/archive/](docs/archive/) 目录

## 项目状态

✅ **当前版本**: v1.0.0-production-ready  
✅ **系统状态**: 🟢 生产就绪  
✅ **测试通过率**: 100% (57/57)  
✅ **代码质量**: ⭐⭐⭐⭐⭐ 优秀

最后更新：2026-01-23