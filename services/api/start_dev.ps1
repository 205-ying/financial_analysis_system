# ==========================================
# 餐饮企业财务分析系统 - 后端开发服务器启动脚本
# ==========================================

Write-Host "==========================================`n" -ForegroundColor Cyan
Write-Host "餐饮企业财务分析系统 - 后端服务启动中...`n" -ForegroundColor Green
Write-Host "==========================================`n" -ForegroundColor Cyan

# 确保在正确的目录
Set-Location $PSScriptRoot

# 检查虚拟环境是否存在
if (-not (Test-Path "venv")) {
    Write-Host "错误: 虚拟环境不存在！" -ForegroundColor Red
    Write-Host "请先运行: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# 激活虚拟环境并启动服务器
Write-Host "启动开发服务器...`n" -ForegroundColor Green
Write-Host "服务器地址: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "API 文档: http://127.0.0.1:8000/docs" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# 设置 PYTHONPATH
$env:PYTHONPATH = "src"

& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
