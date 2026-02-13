"""
重置用户密码脚本

重置系统初始用户（admin, manager, cashier）的密码为默认值

使用方法：
python qa_scripts/tools/backend/reset_passwords.py
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
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User


# 默认用户密码配置
DEFAULT_PASSWORDS = {
    "admin": "Admin@123",
    "manager": "Manager@123",
    "cashier": "Cashier@123"
}


async def reset_password(session: AsyncSession, username: str, new_password: str) -> bool:
    """重置单个用户的密码"""
    result = await session.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        print(f"  ❌ 用户 {username} 不存在")
        return False
    
    # 更新密码
    user.password_hash = hash_password(new_password)
    await session.commit()
    
    print(f"  ✅ 用户 {username} 密码已重置为: {new_password}")
    return True


async def reset_all_passwords():
    """重置所有初始用户的密码"""
    print("=" * 70)
    print("🔑 开始重置用户密码...")
    print("=" * 70)
    print()
    
    async with AsyncSessionLocal() as session:
        success_count = 0
        fail_count = 0
        
        for username, password in DEFAULT_PASSWORDS.items():
            if await reset_password(session, username, password):
                success_count += 1
            else:
                fail_count += 1
        
        print()
        print("=" * 70)
        print("✅ 密码重置完成！")
        print("=" * 70)
        print()
        print(f"📊 统计信息：")
        print(f"  - 成功重置：{success_count} 个用户")
        print(f"  - 失败/不存在：{fail_count} 个用户")
        print()
        print("📋 重置后的用户密码：")
        for username, password in DEFAULT_PASSWORDS.items():
            print(f"  - {username:12s} : {password}")
        print()


async def reset_specific_user(username: str, password: str):
    """重置指定用户的密码"""
    print("=" * 70)
    print(f"🔑 重置用户 {username} 的密码...")
    print("=" * 70)
    print()
    
    async with AsyncSessionLocal() as session:
        await reset_password(session, username, password)
    
    print()


async def reset_all_test_users():
    """重置所有测试用户的密码为 Test@123"""
    print("=" * 70)
    print("🔑 开始重置所有测试用户密码...")
    print("=" * 70)
    print()
    
    async with AsyncSessionLocal() as session:
        # 查找所有测试用户（不包括admin）
        result = await session.execute(
            select(User).where(User.username != "admin")
        )
        test_users = result.scalars().all()
        
        if not test_users:
            print("  ⚠️  没有找到测试用户")
            return
        
        print(f"找到 {len(test_users)} 个测试用户，开始重置...")
        print()
        
        success_count = 0
        new_password = "Test@123"
        
        for user in test_users:
            user.password_hash = hash_password(new_password)
            success_count += 1
            if success_count <= 10:  # 只显示前10个
                print(f"  ✅ {user.username}")
        
        await session.commit()
        
        if success_count > 10:
            print(f"  ... (还重置了 {success_count - 10} 个用户)")
        
        print()
        print("=" * 70)
        print("✅ 所有测试用户密码重置完成！")
        print("=" * 70)
        print()
        print(f"📊 统计信息：")
        print(f"  - 成功重置：{success_count} 个测试用户")
        print(f"  - 统一密码：{new_password}")
        print()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="重置用户密码")
    parser.add_argument(
        "--user", "-u",
        help="指定要重置的用户名（不指定则重置所有初始用户）"
    )
    parser.add_argument(
        "--password", "-p",
        help="指定新密码（与--user一起使用）"
    )
    parser.add_argument(
        "--all-test-users", "-a",
        action="store_true",
        help="重置所有测试用户（除admin外）的密码为 Test@123"
    )
    
    args = parser.parse_args()
    
    try:
        if args.all_test_users:
            # 重置所有测试用户
            await reset_all_test_users()
        elif args.user:
            # 重置指定用户
            if not args.password:
                print("❌ 错误：指定用户时必须提供密码（使用 --password 参数）")
                return
            await reset_specific_user(args.user, args.password)
        else:
            # 重置所有初始用户
            await reset_all_passwords()
    
    except Exception as e:
        print(f"\n❌ 错误：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

