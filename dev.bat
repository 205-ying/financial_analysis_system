@echo off
REM 财务分析系统 - Windows 开发脚本

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="install-backend" goto install-backend
if "%1"=="install-frontend" goto install-frontend
if "%1"=="dev-backend" goto dev-backend
if "%1"=="dev-frontend" goto dev-frontend
if "%1"=="test" goto test
if "%1"=="test-backend" goto test-backend
if "%1"=="lint" goto lint
if "%1"=="lint-backend" goto lint-backend
if "%1"=="lint-frontend" goto lint-frontend
if "%1"=="format" goto format
if "%1"=="format-backend" goto format-backend
if "%1"=="format-frontend" goto format-frontend
if "%1"=="check" goto check
if "%1"=="check-backend" goto check-backend
if "%1"=="check-frontend" goto check-frontend
if "%1"=="migrate" goto migrate
if "%1"=="clean" goto clean
goto unknown

:help
echo 财务分析系统 - 可用命令：
echo.
echo   dev.bat install           安装所有依赖
echo   dev.bat install-backend   安装后端依赖
echo   dev.bat install-frontend  安装前端依赖
echo.
echo   dev.bat dev-backend       启动后端开发服务器
echo   dev.bat dev-frontend      启动前端开发服务器
echo.
echo   dev.bat test              运行所有测试
echo   dev.bat test-backend      运行后端测试
echo.
echo   dev.bat lint              检查所有代码
echo   dev.bat lint-backend      检查后端代码
echo   dev.bat lint-frontend     检查前端代码
echo.
echo   dev.bat format            格式化所有代码
echo   dev.bat format-backend    格式化后端代码
echo   dev.bat format-frontend   格式化前端代码
echo.
echo   dev.bat check             运行所有检查
echo   dev.bat check-backend     运行后端所有检查
echo   dev.bat check-frontend    运行前端所有检查
echo.
echo   dev.bat migrate           运行数据库迁移
echo   dev.bat clean             清理生成文件
echo.
goto end

:install
echo 📦 安装所有依赖...
call :install-backend
call :install-frontend
goto end

:install-backend
echo 📦 安装后端依赖...
cd backend
pip install -r requirements_dev.txt
cd ..
goto end

:install-frontend
echo 📦 安装前端依赖...
cd frontend
call npm install
cd ..
goto end

:dev-backend
echo 🚀 启动后端开发服务器...
cd backend
python dev.py start
cd ..
goto end

:dev-frontend
echo 🚀 启动前端开发服务器...
cd frontend
call npm run dev
cd ..
goto end

:test
echo 🧪 运行所有测试...
call :test-backend
goto end

:test-backend
echo 🧪 运行后端测试...
cd backend
python dev.py test
cd ..
goto end

:lint
echo 🔍 检查所有代码...
call :lint-backend
call :lint-frontend
goto end

:lint-backend
echo 🔍 检查后端代码...
cd backend
python dev.py lint
cd ..
goto end

:lint-frontend
echo 🔍 检查前端代码...
cd frontend
call npm run lint
cd ..
goto end

:format
echo ✨ 格式化所有代码...
call :format-backend
call :format-frontend
goto end

:format-backend
echo ✨ 格式化后端代码...
cd backend
python dev.py format
cd ..
goto end

:format-frontend
echo ✨ 格式化前端代码...
cd frontend
call npm run format
cd ..
goto end

:check
echo ✅ 运行所有检查...
call :check-backend
call :check-frontend
goto end

:check-backend
echo ✅ 运行后端所有检查...
cd backend
python dev.py all
cd ..
goto end

:check-frontend
echo ✅ 运行前端所有检查...
cd frontend
call npm run lint
if errorlevel 1 goto error
call npm run type-check
if errorlevel 1 goto error
cd ..
goto end

:migrate
echo 🗄️ 运行数据库迁移...
cd backend
python dev.py migrate
cd ..
goto end

:clean
echo 🧹 清理生成文件...
if exist backend\__pycache__ rd /s /q backend\__pycache__
if exist backend\.pytest_cache rd /s /q backend\.pytest_cache
if exist backend\.mypy_cache rd /s /q backend\.mypy_cache
if exist backend\htmlcov rd /s /q backend\htmlcov
if exist backend\.coverage del backend\.coverage
if exist frontend\node_modules\.cache rd /s /q frontend\node_modules\.cache
if exist frontend\dist rd /s /q frontend\dist
echo ✅ 清理完成
goto end

:unknown
echo ❌ 未知命令: %1
echo 运行 'dev.bat help' 查看可用命令
goto end

:error
echo ❌ 命令执行失败
exit /b 1

:end
