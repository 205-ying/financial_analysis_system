"""
pytest 配置文件

提供测试所需的 fixtures，包括：
- 数据库连接（使用独立的测试数据库）
- 测试客户端
- 测试用户
"""

import asyncio
import os
from collections.abc import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models.expense import ExpenseType
from app.models.store import Store
from app.models.user import Permission, Role, User

# 测试数据库 URL，优先使用环境变量，便于 CI 和本地按需覆盖。
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/financial_analysis_test",
    ),
)

# 创建测试引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    connect_args={"statement_cache_size": 0},
    poolclass=NullPool,  # 测试时不使用连接池
)

# 创建测试会话工厂
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """创建一个事件循环实例用于整个测试会话"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def _truncate_all_tables() -> None:
    """清空所有测试表并重置自增主键。"""
    table_names = [table.name for table in reversed(Base.metadata.sorted_tables)]
    if not table_names:
        return

    quoted_names = ", ".join(f'"{table_name}"' for table_name in table_names)
    async with test_engine.begin() as conn:
        await conn.execute(
            text(f"TRUNCATE TABLE {quoted_names} RESTART IDENTITY CASCADE")
        )


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database() -> AsyncGenerator[None, None]:
    """整个测试会话只创建一次表，结束时再统一销毁。"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    为每个测试函数创建一个独立的数据库会话
    测试结束后自动回滚所有更改
    """
    await _truncate_all_tables()

    # 创建会话
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

    await _truncate_all_tables()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    创建测试客户端
    自动替换数据库依赖为测试数据库
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(client: AsyncClient) -> AsyncClient:
    """兼容旧测试命名。"""
    return client


@pytest.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """
    创建测试用户（普通用户）
    """
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("test123"),
        full_name="测试用户",
        is_active=True,
        is_superuser=False,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> User:
    """
    创建测试管理员用户
    """
    # 创建管理员角色
    admin_role = Role(code="admin", name="管理员", description="系统管理员")
    db_session.add(admin_role)

    # 创建权限
    permissions = [
        Permission(
            code="dashboard:view",
            name="看板查看",
            resource="dashboard",
            action="view",
            description="查看看板数据",
        ),
        Permission(
            code="order:view",
            name="订单查看",
            resource="order",
            action="view",
            description="查看订单",
        ),
        Permission(
            code="expense:view",
            name="费用查看",
            resource="expense",
            action="view",
            description="查看费用",
        ),
        Permission(
            code="kpi:view",
            name="KPI查看",
            resource="kpi",
            action="view",
            description="查看KPI",
        ),
        Permission(
            code="kpi:rebuild",
            name="KPI重建",
            resource="kpi",
            action="rebuild",
            description="重建KPI数据",
        ),
        Permission(
            code="audit:view",
            name="审计查看",
            resource="audit",
            action="view",
            description="查看审计日志",
        ),
    ]

    for perm in permissions:
        db_session.add(perm)
    admin_role.permissions.extend(permissions)

    await db_session.flush()

    # 创建管理员用户
    admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("admin123"),
        full_name="管理员",
        is_active=True,
        is_superuser=True,
    )
    admin.roles.append(admin_role)

    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)

    return admin


@pytest.fixture(scope="function")
async def test_admin(admin_user: User) -> User:
    """兼容旧测试命名。"""
    return admin_user


@pytest.fixture(scope="function")
async def auth_headers(client: AsyncClient, admin_user: User) -> dict:
    """
    获取认证头（已登录的管理员Token）
    """
    response = await client.post(
        "/api/v1/auth/login", json={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    token = data["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
async def admin_token(auth_headers: dict) -> str:
    """返回管理员访问令牌。"""
    return auth_headers["Authorization"].removeprefix("Bearer ")


@pytest.fixture(scope="function")
async def admin_headers(auth_headers: dict) -> dict:
    """兼容旧测试命名。"""
    return auth_headers


@pytest.fixture(scope="function")
async def test_store(db_session: AsyncSession) -> Store:
    """创建测试门店。"""
    store = Store(
        code="TEST001",
        name="测试门店",
        address="测试地址",
        contact_person="张三",
        phone="13800138000",
        is_active=True,
    )
    db_session.add(store)
    await db_session.commit()
    await db_session.refresh(store)
    return store


@pytest.fixture(scope="function")
async def test_expense_type(db_session: AsyncSession) -> ExpenseType:
    """创建测试费用科目。"""
    expense_type = ExpenseType(
        type_code="RENT",
        name="租金",
        category="operating",
        cost_behavior="fixed",
        description="门店租金费用",
        is_active=True,
    )
    db_session.add(expense_type)
    await db_session.commit()
    await db_session.refresh(expense_type)
    return expense_type
