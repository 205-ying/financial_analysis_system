# 财务分析系统 - Makefile
# 提供统一的项目管理命令

.PHONY: help install dev test lint format check clean

# 默认目标
help:
	@echo "财务分析系统 - 可用命令："
	@echo ""
	@echo "  make install          安装所有依赖"
	@echo "  make install-backend  安装后端依赖"
	@echo "  make install-frontend 安装前端依赖"
	@echo ""
	@echo "  make dev              启动开发环境（前后端）"
	@echo "  make dev-backend      启动后端开发服务器"
	@echo "  make dev-frontend     启动前端开发服务器"
	@echo ""
	@echo "  make test             运行所有测试"
	@echo "  make test-backend     运行后端测试"
	@echo "  make test-frontend    运行前端测试"
	@echo ""
	@echo "  make lint             检查代码质量"
	@echo "  make lint-backend     检查后端代码"
	@echo "  make lint-frontend    检查前端代码"
	@echo ""
	@echo "  make format           格式化代码"
	@echo "  make format-backend   格式化后端代码"
	@echo "  make format-frontend  格式化前端代码"
	@echo ""
	@echo "  make check            运行所有检查"
	@echo "  make check-backend    运行后端所有检查"
	@echo "  make check-frontend   运行前端所有检查"
	@echo ""
	@echo "  make migrate          运行数据库迁移"
	@echo "  make clean            清理生成文件"
	@echo ""

# 安装依赖
install: install-backend install-frontend

install-backend:
	@echo "📦 安装后端依赖..."
	cd services/api && pip install -r requirements_dev.txt

install-frontend:
	@echo "📦 安装前端依赖..."
	cd apps/web && npm install

# 启动开发环境
dev:
	@echo "🚀 启动开发环境..."
	@echo "请在两个终端窗口分别运行："
	@echo "  1. make dev-backend"
	@echo "  2. make dev-frontend"

dev-backend:
	@echo "🚀 启动后端开发服务器..."
	cd services/api && python dev.py start

dev-frontend:
	@echo "🚀 启动前端开发服务器..."
	cd apps/web && npm run dev

# 运行测试
test: test-backend test-frontend

test-backend:
	@echo "🧪 运行后端测试..."
	cd services/api && python dev.py test

test-frontend:
	@echo "🧪 运行前端测试..."
	cd apps/web && npm run test

# 代码检查
lint: lint-backend lint-frontend

lint-backend:
	@echo "🔍 检查后端代码..."
	cd services/api && python dev.py lint

lint-frontend:
	@echo "🔍 检查前端代码..."
	cd apps/web && npm run lint

# 代码格式化
format: format-backend format-frontend

format-backend:
	@echo "✨ 格式化后端代码..."
	cd services/api && python dev.py format

format-frontend:
	@echo "✨ 格式化前端代码..."
	cd apps/web && npm run format

# 运行所有检查
check: check-backend check-frontend

check-backend:
	@echo "✅ 运行后端所有检查..."
	cd services/api && python dev.py all

check-frontend:
	@echo "✅ 运行前端所有检查..."
	cd apps/web && npm run lint && npm run type-check && npm run build

# 数据库迁移
migrate:
	@echo "🗄️  运行数据库迁移..."
	cd services/api && python dev.py migrate

# 清理
clean:
	@echo "🧹 清理生成文件..."
	rm -rf services/api/__pycache__
	rm -rf services/api/**/__pycache__
	rm -rf services/api/.pytest_cache
	rm -rf services/api/.mypy_cache
	rm -rf services/api/htmlcov
	rm -rf services/api/.coverage
	rm -rf apps/web/node_modules/.cache
	rm -rf apps/web/dist
	@echo "✅ 清理完成"

# 构建
build: build-frontend

build-frontend:
	@echo "🏗️  构建前端..."
	cd apps/web && npm run build

# 类型检查
type-check: type-check-backend type-check-frontend

type-check-backend:
	@echo "🔤 后端类型检查..."
	cd services/api && python dev.py type-check

type-check-frontend:
	@echo "🔤 前端类型检查..."
	cd apps/web && npm run type-check
