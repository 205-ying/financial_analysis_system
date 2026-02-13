"""检查audit_log表的实际结构"""
import asyncio
import os
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
BACKEND_DIR = PROJECT_ROOT / "backend"
load_dotenv(BACKEND_DIR / ".env")

async def check_audit_log_columns():
    database_url = os.getenv("DATABASE_URL")
    async_engine = create_async_engine(database_url, echo=False)
    
    async with async_engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'audit_log'
            ORDER BY ordinal_position;
        """))
        
        print("\n审计日志表实际列结构：")
        print("-" * 80)
        for row in result:
            print(f"{row.column_name:20} {row.data_type:20} NULL={row.is_nullable:5} DEFAULT={row.column_default}")
        print("-" * 80)
    
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(check_audit_log_columns())
