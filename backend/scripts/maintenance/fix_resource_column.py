"""
修复 audit_log 表的 resource 字段约束
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine


async def fix_resource_column():
    print("修复 audit_log.resource 字段...")
    async with engine.begin() as conn:
        # 将 resource 字段改为允许 NULL
        print("将 resource 字段改为 nullable...")
        await conn.execute(text("""
            ALTER TABLE audit_log 
            ALTER COLUMN resource DROP NOT NULL
        """))
        print("✅ resource 字段已改为允许 NULL")
        
        # 由于 resource 和 resource_type 功能重复，将现有 resource 数据复制到 resource_type
        print("\n复制 resource 数据到 resource_type...")
        await conn.execute(text("""
            UPDATE audit_log 
            SET resource_type = resource 
            WHERE resource_type IS NULL AND resource IS NOT NULL
        """))
        print("✅ 数据已迁移")
        
        print("\n✅ 修复完成！")


if __name__ == "__main__":
    asyncio.run(fix_resource_column())
