"""
修复 audit_log 表结构

添加缺失的字段以匹配模型定义
"""
import asyncio
from sqlalchemy import text
from app.core.database import engine


async def fix_audit_log_table():
    """修复audit_log表结构"""
    async with engine.begin() as conn:
        print("开始修复 audit_log 表结构...")
        
        # 检查表是否存在
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'audit_log'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print("❌ audit_log 表不存在，请先运行迁移")
            return
        
        print("✅ audit_log 表存在，检查缺失字段...")
        
        # 获取当前表的所有列
        result = await conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'audit_log';
        """))
        existing_columns = {row[0] for row in result.fetchall()}
        print(f"现有字段: {existing_columns}")
        
        # 定义需要的字段及其SQL定义
        required_fields = {
            'resource': "ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS resource VARCHAR(50);",
            'resource_type': "ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS resource_type VARCHAR(50);",
            'method': "ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS method VARCHAR(10);",
            'path': "ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS path VARCHAR(255);",
            'status': "ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'success';",
            'status_code': "ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS status_code INTEGER;",
            'updated_at': "ALTER TABLE audit_log ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP;",
        }
        
        # 添加缺失的字段
        for field, sql in required_fields.items():
            if field not in existing_columns:
                print(f"添加字段: {field}")
                await conn.execute(text(sql))
                print(f"✅ 已添加字段: {field}")
            else:
                print(f"⏭️  字段已存在: {field}")
        
        print("✅ audit_log 表结构修复完成！")


if __name__ == "__main__":
    asyncio.run(fix_audit_log_table())

