"""
修复 audit_log 表的 detail 字段类型

将 detail 字段从 jsonb 改为 text
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine


async def fix_detail_column_type():
    """修复detail字段类型"""
    async with engine.begin() as conn:
        print("修复 audit_log.detail 字段类型...")
        
        # 检查当前字段类型
        result = await conn.execute(text("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'audit_log' AND column_name = 'detail';
        """))
        current_type = result.scalar()
        print(f"当前 detail 字段类型: {current_type}")
        
        if current_type == 'jsonb':
            print("将 detail 字段从 jsonb 改为 text...")
            await conn.execute(text(
                "ALTER TABLE audit_log ALTER COLUMN detail TYPE text USING detail::text;"
            ))
            print("✅ detail 字段类型已更新为 text")
        elif current_type == 'text':
            print("✅ detail 字段已经是 text 类型")
        else:
            print(f"⚠️  detail 字段类型为 {current_type}，将改为 text...")
            await conn.execute(text(
                "ALTER TABLE audit_log ALTER COLUMN detail TYPE text;"
            ))
            print("✅ detail 字段类型已更新为 text")


if __name__ == "__main__":
    asyncio.run(fix_detail_column_type())

