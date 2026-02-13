#!/usr/bin/env python
"""测试数据库连接"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine

async def test_db():
    print("测试数据库连接...")
    DATABASE_URL = "postgresql+asyncpg://postgres:199697@localhost:5432/financial_analysis"
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            print(f"✅ 数据库连接成功！结果: {result.scalar()}")
        await engine.dispose()
    except Exception as e:
        print(f"❌ 数据库连接失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_db())
