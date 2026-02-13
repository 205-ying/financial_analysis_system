"""
标记alembic迁移为已完成

由于表已手动修复，需要更新alembic版本表
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine


async def mark_migration_done():
    """标记audit_log迁移已完成"""
    async with engine.begin() as conn:
        print("检查alembic_version表...")
        
        # 检查当前版本
        result = await conn.execute(text("SELECT version_num FROM alembic_version;"))
        current_version = result.scalar()
        print(f"当前数据库版本: {current_version}")
        
        target_version = "0002_audit_log"
        
        if current_version == target_version:
            print(f"✅ 数据库已是最新版本: {target_version}")
        else:
            print(f"更新版本从 {current_version} 到 {target_version}...")
            await conn.execute(text(
                f"UPDATE alembic_version SET version_num = '{target_version}';"
            ))
            print(f"✅ 版本已更新到: {target_version}")


if __name__ == "__main__":
    asyncio.run(mark_migration_done())

