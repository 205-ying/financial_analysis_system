"""
Alembic 环境配置脚本

配置 Alembic 数据库迁移环境，支持异步数据库操作
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# 这是 Alembic Config 对象，提供对 .ini 文件的访问
config = context.config

# 如果配置了日志，则解析配置文件中的日志设置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 导入应用配置和模型基类
# 注意：这里使用相对导入路径，确保能正确导入
try:
    import sys
    import os
    # 添加项目根目录到 Python 路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    
    from app.core.config import settings
    from app.core.database import Base
    
    # 添加模型的 MetaData 对象以支持 'autogenerate'
    target_metadata = Base.metadata
except ImportError:
    # 如果导入失败，使用空的 metadata（手动迁移模式）
    target_metadata = None

# 其他从 env.py 中需要的值，由需要访问脚本的值定义。
# my_important_option = config.get_main_option("my_important_option")
# ... 等等。


def run_migrations_offline() -> None:
    """
    离线模式运行迁移
    
    这种配置了"离线"模式，在这种模式下我们不实际连接到数据库，
    而是把迁移配置成使用 URL 来生成 DDL 语句。
    """
    # 从配置中获取数据库 URL，如果没有设置，则使用应用配置
    url = config.get_main_option("sqlalchemy.url")
    if url is None and 'settings' in globals():
        # 将异步 URL 转换为同步 URL 用于离线模式
        url = settings.database_url.replace("+asyncpg", "")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 在这里添加自定义的配置选项
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """执行迁移的核心函数"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # 在这里添加自定义的配置选项
        compare_type=True,
        compare_server_default=True,
        # 渲染模式配置
        render_as_batch=False,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    异步模式运行迁移
    
    这种模式用于异步数据库引擎。
    """
    # 创建异步配置副本
    configuration = config.get_section(config.config_ini_section, {})
    
    # 如果没有配置数据库 URL，使用应用配置
    if not configuration.get("sqlalchemy.url") and 'settings' in globals():
        configuration["sqlalchemy.url"] = settings.database_url

    # 创建异步引擎
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # 在异步引擎上运行迁移
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    在线模式运行迁移
    
    这种模式下我们需要创建一个引擎并将连接与上下文关联。
    """
    # 检查是否可以使用异步模式
    if 'settings' in globals() and "+asyncpg" in getattr(settings, 'database_url', ''):
        # 运行异步迁移
        asyncio.run(run_async_migrations())
    else:
        # 回退到同步模式
        from sqlalchemy import engine_from_config
        
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection, 
                target_metadata=target_metadata,
                compare_type=True,
                compare_server_default=True,
            )

            with context.begin_transaction():
                context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
