"""
数据库连接管理模块

配置 SQLAlchemy 异步数据库引擎和会话，
支持连接池管理和事务处理。
"""

from typing import AsyncGenerator

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings
from app.models.base import Base


# 创建异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.database_echo,  # 是否打印 SQL 语句
    pool_pre_ping=True,  # 连接前检查连接是否有效
    pool_recycle=3600,   # 连接回收时间（秒）
    pool_size=10,        # 连接池大小
    max_overflow=20,     # 连接池溢出大小
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 事务提交后不过期对象
    autoflush=False,         # 不自动刷新
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话的依赖注入函数
    
    用于 FastAPI 依赖注入系统，确保每个请求都有独立的数据库会话，
    并在请求结束后正确关闭会话。
    
    Yields:
        AsyncSession: 异步数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    """
    创建数据库表
    
    在应用启动时调用，用于创建数据库表结构。
    生产环境建议使用 Alembic 进行数据库迁移管理。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables():
    """
    删除数据库表
    
    主要用于测试环境清理数据。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话
    
    用于依赖注入，自动管理数据库会话的创建和关闭。
    
    Yields:
        AsyncSession: 异步数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()