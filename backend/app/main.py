"""
FastAPI 应用主入口

配置和启动 FastAPI 应用，包含中间件、异常处理器、路由注册等
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time

from app.core.config import settings
from app.core.database import create_tables, engine
from app.core.logging import configure_logging
from app.core.exceptions import (
    BaseAPIException,
    base_api_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    应用生命周期管理
    
    在应用启动和关闭时执行必要的初始化和清理工作
    """
    # 启动时执行
    logger.info("🚀 应用启动中...")
    
    # 配置日志
    configure_logging()
    logger.info("✅ 日志系统配置完成")
    
    # 可选：创建数据库表（生产环境建议使用 Alembic）
    if settings.environment == "development":
        try:
            await create_tables()
            logger.info("✅ 数据库表创建完成")
        except Exception as e:
            logger.error(f"❌ 数据库表创建失败: {e}")
    
    logger.info(f"🎉 应用启动成功！运行环境: {settings.environment}")
    
    yield
    
    # 关闭时执行
    logger.info("🔄 应用关闭中...")
    
    # 关闭数据库连接
    await engine.dispose()
    logger.info("✅ 数据库连接已关闭")
    
    logger.info("👋 应用已关闭")


def create_application() -> FastAPI:
    """
    创建 FastAPI 应用实例
    
    Returns:
        FastAPI: 配置好的应用实例
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="餐饮企业财务分析与可视化系统 API",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    
    # 配置中间件
    setup_middleware(app)
    
    # 配置异常处理器
    setup_exception_handlers(app)
    
    # 注册路由
    setup_routes(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """
    配置中间件
    
    Args:
        app: FastAPI 应用实例
    
    注意：中间件的添加顺序与执行顺序相反，
    最后添加的中间件会最先执行（洋葱模型）
    """
    
    # CORS 中间件 - 最后添加，最先执行
    # 这样可以处理 OPTIONS 预检请求
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )
    
    # 信任的主机中间件（安全）
    if settings.environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
        )
    
    # 请求处理时间中间件 - 最先添加，最后执行
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        """添加请求处理时间到响应头"""
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # 记录请求日志
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s"
        )
        
        return response


def setup_exception_handlers(app: FastAPI) -> None:
    """
    配置异常处理器
    
    Args:
        app: FastAPI 应用实例
    """
    from fastapi import HTTPException
    from fastapi.exceptions import RequestValidationError
    
    # 自定义异常处理器
    app.add_exception_handler(BaseAPIException, base_api_exception_handler)
    
    # HTTP 异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # 数据验证异常处理器
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 通用异常处理器
    app.add_exception_handler(Exception, general_exception_handler)


def setup_routes(app: FastAPI) -> None:
    """
    配置路由
    
    Args:
        app: FastAPI 应用实例
    """
    # 注册 API 路由
    app.include_router(
        api_router,
        prefix=settings.api_v1_prefix
    )
    
    # 根路径重定向到文档
    @app.get("/", include_in_schema=False)
    async def root():
        """根路径重定向"""
        return JSONResponse(
            content={
                "message": f"欢迎使用 {settings.app_name}",
                "version": settings.app_version,
                "docs_url": "/docs",
                "api_version": "v1",
                "api_prefix": settings.api_v1_prefix,
            }
        )


# 创建应用实例
app = create_application()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
