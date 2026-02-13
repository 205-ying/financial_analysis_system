@echo off
REM 预算管理功能快速测试脚本
REM 用于Windows环境

echo ========================================
echo 预算管理功能测试工具
echo ========================================
echo.

cd /d %~dp0..

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 未找到虚拟环境，请先创建: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

echo [1/5] 检查环境...
python --version
echo.

echo [2/5] 生成测试数据...
python scripts\generate_budget_test_data.py
if errorlevel 1 (
    echo [错误] 测试数据生成失败
    pause
    exit /b 1
)
echo.

echo [3/5] 运行单元测试...
pytest tests\test_budget.py -v --tb=short
if errorlevel 1 (
    echo [警告] 部分测试未通过
)
echo.

echo [4/5] 生成覆盖率报告...
pytest tests\test_budget.py --cov=app.services.budget_service --cov=app.api.v1.budgets --cov-report=html --cov-report=term
echo.

echo [5/5] 测试完成！
echo.
echo 查看详细报告:
echo   - 测试报告: 查看上方输出
echo   - 覆盖率报告: start htmlcov\index.html
echo   - 测试指南: docs\budget_testing_guide.md
echo.

pause
