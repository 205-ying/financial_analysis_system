@echo off
chcp 65001 > nul

echo ==========================================
echo 餐饮企业财务分析系统启动脚本 (Windows)
echo ==========================================

:: 检查 Python 版本
echo 检查 Python 版本...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo Python 未安装或不在 PATH 中
    pause
    exit /b 1
)

:: 检查 Node.js 版本
echo 检查 Node.js 版本...
node --version
if %ERRORLEVEL% NEQ 0 (
    echo Node.js 未安装或不在 PATH 中
    pause
    exit /b 1
)

echo ==========================================
echo 启动后端服务 (端口: 8000)...
echo ==========================================
cd /d "%~dp0..\backend"

:: 检查虚拟环境
if not exist "venv" (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

:: 安装依赖
echo 安装 Python 依赖...
pip install -r requirements.txt

:: 检查环境变量文件
if not exist ".env" (
    echo 创建环境变量文件...
    copy .env.example .env
    echo 请修改 .env 文件中的数据库连接信息
    echo 然后重新运行启动脚本
    pause
    exit /b 1
)

:: 数据库迁移
echo 执行数据库迁移...
:: alembic upgrade head

echo 启动后端服务...
start "后端服务" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

cd ..

echo ==========================================
echo 启动前端服务 (端口: 3000)...
echo ==========================================
cd /d "%~dp0..\frontend"

:: 安装依赖
if not exist "node_modules" (
    echo 安装 Node.js 依赖...
    npm install
)

:: 检查环境变量文件
if not exist ".env.development" (
    echo 创建前端环境变量文件...
    copy .env.example .env.development
)

echo 启动前端服务...
start "前端服务" cmd /k "npm run dev"

cd /d "%~dp0"

echo ==========================================
echo 服务启动完成！
echo ==========================================
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8000
echo API 文档: http://localhost:8000/docs
echo.
echo 按任意键退出...
echo ==========================================
pause