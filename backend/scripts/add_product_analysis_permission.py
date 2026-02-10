"""
添加菜品分析权限

如果数据库已经初始化过，运行此脚本补充 product_analysis:view 权限。
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import Permission


async def add_product_analysis_permission():
    async with AsyncSessionLocal() as session:
        # 检查是否已存在
        result = await session.execute(
            select(Permission).where(Permission.code == "product_analysis:view")
        )
        if result.scalar_one_or_none():
            print("✅ product_analysis:view 权限已存在，无需添加")
            return

        perm = Permission(
            code="product_analysis:view",
            name="查看菜品分析",
            resource="product_analysis",
            action="view",
            description="查看菜品销售分析报表",
        )
        session.add(perm)
        await session.commit()
        print("✅ 已添加 product_analysis:view 权限")


if __name__ == "__main__":
    asyncio.run(add_product_analysis_permission())
