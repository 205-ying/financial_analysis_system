@echo off
echo ==========================================
echo 餐饮企业财务分析系统 - 后端服务启动
echo ==========================================
echo.
echo 启动开发服务器...
echo 服务器地址: http://127.0.0.1:8000
echo API 文档: http://127.0.0.1:8000/docs
echo.
echo ==========================================
echo.

cd /d "%~dp0"
set PYTHONPATH=src
call venv\Scripts\activate.bat
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
