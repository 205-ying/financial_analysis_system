#!/usr/bin/env python3
"""
验证数据库 cost_behavior 字段是否成功添加
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_cost_behavior_field():
    """测试 cost_behavior 字段是否存在并且可以查询"""
    print("🔍 测试 ExpenseType 表的 cost_behavior 字段...")
    
    # 使用与项目相同的数据库连接
    DATABASE_URL = "postgresql+asyncpg://postgres:199697@localhost:5432/financial_analysis"
    
    try:
        engine = create_async_engine(DATABASE_URL, echo=False)
        async with engine.connect() as conn:
            # 测试查询 expense_type 表结构
            result = await conn.execute(text("""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'expense_type' 
                AND column_name = 'cost_behavior'
            """))
            
            column_info = result.fetchone()
            if column_info:
                print(f"✅ cost_behavior 字段已存在:")
                print(f"   列名: {column_info[0]}")
                print(f"   数据类型: {column_info[1]}")
                print(f"   是否可空: {column_info[2]}")
                print(f"   默认值: {column_info[3]}")
            else:
                print("❌ cost_behavior 字段不存在")
                await engine.dispose()
                return False
            
            # 测试查询 expense_type 表数据
            print("\n🔍 测试查询 expense_type 数据...")
            result = await conn.execute(text("""
                SELECT id, name, cost_behavior 
                FROM expense_type 
                LIMIT 5
            """))
            
            rows = result.fetchall()
            if rows:
                print("✅ 成功查询到数据:")
                for row in rows:
                    print(f"   ID: {row[0]}, 名称: {row[1]}, 成本习性: {row[2]}")
            else:
                print("ℹ️  表中暂无数据")
            
            print("\n✅ 数据库迁移验证成功！cost_behavior 字段正常工作")
            await engine.dispose()
            return True
            
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_cost_behavior_field())
        if result:
            print("\n🎉 数据库迁移修复成功！ExpenseType.cost_behavior 字段已正常工作")
        else:
            print("\n💥 数据库迁移仍有问题")
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")