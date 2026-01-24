"""
健康检查 API 模块

提供系统健康状态检查接口
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db


router = APIRouter()


@router.get("/health", response_model=Dict[str, Any])
async def health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    健康检查接口
    
    检查服务状态和数据库连接
    
    Returns:
        Dict[str, Any]: 健康状态信息
    """
    health_status = {
        "status": "ok",
        "service": "financial_analysis_system",
        "version": "1.0.0",
        "timestamp": None,
        "checks": {
            "database": "unknown",
            "memory": "ok",
        }
    }
    
    # 添加时间戳
    from datetime import datetime
    health_status["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    # 检查数据库连接
    try:
        result = await db.execute(text("SELECT 1"))
        if result:
            health_status["checks"]["database"] = "ok"
        else:
            health_status["checks"]["database"] = "error"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["database"] = "error"
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
    
    return health_status


@router.get("/health/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> Dict[str, str]:
    """
    就绪状态检查
    
    检查服务是否准备好接收请求
    
    Returns:
        Dict[str, str]: 就绪状态
    """
    try:
        # 检查数据库连接
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not_ready"}


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """
    存活状态检查
    
    检查服务是否正在运行
    
    Returns:
        Dict[str, str]: 存活状态
    """
    return {"status": "alive"}