@echo off
REM 一键启用预算管理模块
REM Windows批处理脚本

echo ========================================
echo 预算管理模块 - 一键启用工具
echo ========================================
echo.

cd /d %~dp0..

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境
    echo 请先创建虚拟环境: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/3] 激活虚拟环境...
call venv\Scripts\activate.bat
echo.

REM 添加权限
echo [2/3] 添加预算管理权限到数据库...
python scripts\add_budget_permissions.py
if errorlevel 1 (
    echo.
    echo [错误] 权限添加失败
    echo 请检查数据库连接是否正常
    pause
    exit /b 1
)
echo.

REM 提示信息
echo [3/3] 完成！
echo.
echo ========================================
echo 预算管理模块已启用
echo ========================================
echo.
echo 下一步操作:
echo   1. 重启后端服务（终端中按 Ctrl+C 停止，然后运行: uvicorn app.main:app --reload）
echo   2. 刷新浏览器（按 F5 或 Ctrl+F5）
echo   3. 重新登录系统
echo   4. 在左侧菜单中查看"预算管理"
echo.
echo 测试数据生成（可选）:
echo   python scripts\generate_budget_test_data.py
echo.
echo 详细文档:
echo   docs\enable_budget_module.md
echo   docs\budget_testing_guide.md
echo.

pause
