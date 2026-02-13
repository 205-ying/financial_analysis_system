"""
查看数据库中的用户列表
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve()
while project_root != project_root.parent and not (project_root / "backend" / "app").exists():
    project_root = project_root.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User


async def list_users():
    """列出所有用户"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        print("\n数据库中的用户列表:")
        print("-" * 60)
        for user in users:
            print(f"ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}, 超级管理员: {user.is_superuser}")
        print("-" * 60)
        print(f"总共 {len(users)} 个用户")


if __name__ == "__main__":
    asyncio.run(list_users())

