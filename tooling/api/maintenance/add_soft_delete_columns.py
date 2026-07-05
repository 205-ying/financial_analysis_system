"""
添加软删除字段到所有需要的表
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).resolve()
while project_root != project_root.parent and not (project_root / "services" / "api" / "app").exists():
    project_root = project_root.parent
backend_dir = project_root / "services" / "api"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def add_soft_delete_columns():
    """为所有需要软删除的表添加字段"""
    async with AsyncSessionLocal() as session:
        try:
            # 需要添加软删除字段的表列表
            tables = ['store', 'product', 'product_category']
            
            for table in tables:
                # 添加 is_deleted 字段
                try:
                    await session.execute(text(f"""
                        ALTER TABLE {table} 
                        ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE NOT NULL
                    """))
                    print(f"✅ 为 {table} 添加 is_deleted 字段")
                except Exception as e:
                    print(f"⚠️  {table}.is_deleted 已存在或添加失败: {str(e)[:100]}")
                
                # 为 product_category 添加 deleted_at 字段（store和product已有）
                if table == 'product_category':
                    try:
                        await session.execute(text(f"""
                            ALTER TABLE {table} 
                            ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE
                        """))
                        print(f"✅ 为 {table} 添加 deleted_at 字段")
                    except Exception as e:
                        print(f"⚠️  {table}.deleted_at 已存在或添加失败: {str(e)[:100]}")
            
            await session.commit()
            print("\n🎉 软删除字段添加完成！")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 操作失败: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(add_soft_delete_columns())

