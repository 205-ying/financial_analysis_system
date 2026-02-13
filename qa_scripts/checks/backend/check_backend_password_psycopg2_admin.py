"""通过 psycopg2 直连检查 admin 口令哈希（仅开发排障使用）。"""

import os

import bcrypt
import psycopg2


def main() -> None:
    connection = psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        database=os.getenv("PGDATABASE", "financial_analysis"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "postgres"),
    )

    cursor = connection.cursor()
    cursor.execute("SELECT id, username, password_hash, is_active FROM users WHERE username = 'admin'")
    row = cursor.fetchone()

    if row is None:
        print("❌ admin 用户不存在")
    else:
        user_id, username, password_hash, is_active = row
        print(f"用户ID: {user_id}")
        print(f"用户名: {username}")
        print(f"激活状态: {is_active}")
        print(f"密码哈希: {password_hash[:50]}...")

        test_password = "Admin@123"
        is_valid = bcrypt.checkpw(test_password.encode("utf-8"), password_hash.encode("utf-8"))
        print(f"\n测试口令 {test_password} 验证结果: {is_valid}")

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
