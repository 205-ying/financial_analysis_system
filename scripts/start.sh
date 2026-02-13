#!/bin/bash

# 餐饮企业财务分析系统 - 启动脚本

echo "=========================================="
echo "餐饮企业财务分析系统启动脚本"
echo "=========================================="

# 检查 Python 版本
echo "检查 Python 版本..."
python_version=$(python --version 2>&1)
echo "Python 版本: $python_version"

# 检查 Node.js 版本
echo "检查 Node.js 版本..."
node_version=$(node --version 2>&1)
echo "Node.js 版本: $node_version"

# 检查 PostgreSQL
echo "检查 PostgreSQL 连接..."
# 这里可以添加数据库连接检查逻辑

echo "=========================================="
echo "启动后端服务 (端口: 8000)..."
echo "=========================================="
cd backend

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装 Python 依赖..."
pip install -r requirements.txt

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo "创建环境变量文件..."
    cp .env.example .env
    echo "请修改 .env 文件中的数据库连接信息"
    echo "然后重新运行启动脚本"
    exit 1
fi

# 数据库迁移
echo "执行数据库迁移..."
# alembic upgrade head

echo "启动后端服务..."
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload &

cd ..

echo "=========================================="
echo "启动前端服务 (端口: 3000)..."
echo "=========================================="
cd frontend

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装 Node.js 依赖..."
    npm install
fi

# 检查环境变量文件
if [ ! -f ".env.development" ]; then
    echo "创建前端环境变量文件..."
    cp .env.example .env.development
fi

echo "启动前端服务..."
npm run dev &

cd ..

echo "=========================================="
echo "服务启动完成！"
echo "=========================================="
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:8000"
echo "API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo "=========================================="

# 等待用户停止
wait