"""
测试门店级数据权限
"""
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient

from app.core.security import hash_password
from app.models.user import User
from app.models.expense import ExpenseRecord, ExpenseType
from app.models.order import OrderHeader
from app.models.store import Store
from app.models.user_store import UserStorePermission


@pytest.mark.asyncio
async def test_manager_restricted_to_store_a(async_client: AsyncClient, db_session, test_user):
    """测试：manager被授权门店A时，只能看到门店A的数据"""
    # 创建两个门店
    store_a = Store(
        code="TEST_A",
        name="测试门店A",
        address="测试地址A",
        is_active=True
    )
    store_b = Store(
        code="TEST_B",
        name="测试门店B",
        address="测试地址B",
        is_active=True
    )
    db_session.add_all([store_a, store_b])
    await db_session.commit()
    await db_session.refresh(store_a)
    await db_session.refresh(store_b)
    
    # 为manager分配门店A的权限
    permission = UserStorePermission(
        user_id=test_user.id,
        store_id=store_a.id
    )
    db_session.add(permission)
    await db_session.commit()
    
    # 创建两个门店的订单
    order_a = OrderHeader(
        order_no="ORD_A_001",
        store_id=store_a.id,
        biz_date=date.today(),
        channel="dine_in",
        gross_amount=Decimal("100.00"),
        net_amount=Decimal("100.00"),
        service_charge=Decimal("0.00"),
        delivery_fee=Decimal("0.00"),
        payment_method="cash",
        order_time=datetime.combine(date.today(), datetime.min.time())
    )
    order_b = OrderHeader(
        order_no="ORD_B_001",
        store_id=store_b.id,
        biz_date=date.today(),
        channel="dine_in",
        gross_amount=Decimal("200.00"),
        net_amount=Decimal("200.00"),
        service_charge=Decimal("0.00"),
        delivery_fee=Decimal("0.00"),
        payment_method="cash",
        order_time=datetime.combine(date.today(), datetime.min.time())
    )
    db_session.add_all([order_a, order_b])
    await db_session.commit()
    
    # 登录manager
    login_response = await async_client.post("/api/v1/auth/login", json={
        "username": test_user.username,
        "password": "test123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试1：查询订单列表（不传store_id），应只返回门店A的订单
    response = await async_client.get("/api/v1/orders", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 1
    assert data["items"][0]["store_id"] == store_a.id
    assert data["items"][0]["order_no"] == "ORD_A_001"
    
    # 测试2：查询门店A的订单（传store_id=A），应成功
    response = await async_client.get(f"/api/v1/orders?store_id={store_a.id}", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 1
    
    # 测试3：查询门店B的订单（传store_id=B），应返回403
    response = await async_client.get(f"/api/v1/orders?store_id={store_b.id}", headers=headers)
    assert response.status_code == 403
    assert "无权访问" in response.json()["message"]


@pytest.mark.asyncio
async def test_admin_can_access_all_stores(async_client: AsyncClient, db_session, test_admin):
    """测试：admin用户可以访问所有门店"""
    # 创建两个门店
    store_a = Store(code="ADMIN_A", name="Admin测试A", address="地址A", is_active=True)
    store_b = Store(code="ADMIN_B", name="Admin测试B", address="地址B", is_active=True)
    db_session.add_all([store_a, store_b])
    await db_session.commit()
    await db_session.refresh(store_a)
    await db_session.refresh(store_b)
    
    # 创建两个门店的订单
    order_a = OrderHeader(
        order_no="ADMIN_ORD_A",
        store_id=store_a.id,
        biz_date=date.today(),
        channel="takeout",
        gross_amount=Decimal("150.00"),
        net_amount=Decimal("150.00"),
        service_charge=Decimal("0.00"),
        delivery_fee=Decimal("0.00"),
        payment_method="cash",
        order_time=datetime.combine(date.today(), datetime.min.time())
    )
    order_b = OrderHeader(
        order_no="ADMIN_ORD_B",
        store_id=store_b.id,
        biz_date=date.today(),
        channel="takeout",
        gross_amount=Decimal("250.00"),
        net_amount=Decimal("250.00"),
        service_charge=Decimal("0.00"),
        delivery_fee=Decimal("0.00"),
        payment_method="cash",
        order_time=datetime.combine(date.today(), datetime.min.time())
    )
    db_session.add_all([order_a, order_b])
    await db_session.commit()
    
    # 登录admin
    login_response = await async_client.post("/api/v1/auth/login", json={
        "username": test_admin.username,
        "password": "admin123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试：查询所有订单，应返回两个门店的数据
    response = await async_client.get("/api/v1/orders", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 2  # 至少包含两个订单
    
    # 验证可以查询门店A
    response_a = await async_client.get(f"/api/v1/orders?store_id={store_a.id}", headers=headers)
    assert response_a.status_code == 200
    
    # 验证可以查询门店B
    response_b = await async_client.get(f"/api/v1/orders?store_id={store_b.id}", headers=headers)
    assert response_b.status_code == 200


@pytest.mark.asyncio
async def test_user_without_permission_has_full_access(async_client: AsyncClient, db_session):
    """测试：没有门店权限记录的用户默认可访问所有门店（向后兼容）"""
    # 创建一个新用户，不分配门店权限
    user = User(
        username="nostore",
        email="nostore@test.com",
        password_hash=hash_password("test123"),
        full_name="无门店权限用户",
        is_active=True,
        is_superuser=False
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # 创建门店和订单
    store = Store(code="NS_STORE", name="测试门店", address="地址", is_active=True)
    db_session.add(store)
    await db_session.commit()
    await db_session.refresh(store)
    
    order = OrderHeader(
        order_no="NS_ORD_001",
        store_id=store.id,
        biz_date=date.today(),
        channel="dine_in",
        gross_amount=Decimal("100.00"),
        net_amount=Decimal("100.00"),
        service_charge=Decimal("0.00"),
        delivery_fee=Decimal("0.00"),
        payment_method="cash",
        order_time=datetime.combine(date.today(), datetime.min.time())
    )
    db_session.add(order)
    await db_session.commit()
    
    # 登录
    login_response = await async_client.post("/api/v1/auth/login", json={
        "username": "nostore",
        "password": "test123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试：可以查询所有订单
    response = await async_client.get("/api/v1/orders", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_expense_records_data_scope(async_client: AsyncClient, db_session, test_user):
    """测试：费用记录也受数据权限限制"""
    # 创建门店
    store_a = Store(code="EXP_A", name="费用门店A", address="地址A", is_active=True)
    store_b = Store(code="EXP_B", name="费用门店B", address="地址B", is_active=True)
    db_session.add_all([store_a, store_b])
    await db_session.commit()
    await db_session.refresh(store_a)
    await db_session.refresh(store_b)
    
    # 分配门店A权限
    permission = UserStorePermission(user_id=test_user.id, store_id=store_a.id)
    db_session.add(permission)
    
    # 创建费用类型
    expense_type = ExpenseType(
        type_code="TEST_EXP",
        name="测试费用",
        category="expense",
        cost_behavior="variable",
        is_active=True
    )
    db_session.add(expense_type)
    await db_session.commit()
    await db_session.refresh(expense_type)
    
    # 创建两个门店的费用记录
    expense_a = ExpenseRecord(
        store_id=store_a.id,
        expense_type_id=expense_type.id,
        biz_date=date.today(),
        amount=Decimal("500.00"),
        created_by=test_user.id
    )
    expense_b = ExpenseRecord(
        store_id=store_b.id,
        expense_type_id=expense_type.id,
        biz_date=date.today(),
        amount=Decimal("600.00"),
        created_by=test_user.id
    )
    db_session.add_all([expense_a, expense_b])
    await db_session.commit()
    
    # 登录
    login_response = await async_client.post("/api/v1/auth/login", json={
        "username": test_user.username,
        "password": "test123"
    })
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试：查询费用列表，应只返回门店A的费用
    response = await async_client.get("/api/v1/expense-records", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 1
    assert data["items"][0]["store_id"] == store_a.id


@pytest.mark.asyncio
async def test_kpi_data_scope(async_client: AsyncClient, db_session, test_user):
    """测试：KPI查询也受数据权限限制"""
    # 创建门店
    store_a = Store(code="KPI_A", name="KPI门店A", address="地址A", is_active=True)
    store_b = Store(code="KPI_B", name="KPI门店B", address="地址B", is_active=True)
    db_session.add_all([store_a, store_b])
    await db_session.commit()
    await db_session.refresh(store_a)
    await db_session.refresh(store_b)
    
    # 分配门店A权限
    permission = UserStorePermission(user_id=test_user.id, store_id=store_a.id)
    db_session.add(permission)
    await db_session.commit()
    
    # 创建KPI数据
    from app.models.kpi import KpiDailyStore
    kpi_a = KpiDailyStore(
        store_id=store_a.id,
        biz_date=date.today(),
        revenue=Decimal("1000.00"),
        order_count=10
    )
    kpi_b = KpiDailyStore(
        store_id=store_b.id,
        biz_date=date.today(),
        revenue=Decimal("2000.00"),
        order_count=20
    )
    db_session.add_all([kpi_a, kpi_b])
    await db_session.commit()
    
    # 登录
    login_response = await async_client.post("/api/v1/auth/login", json={
        "username": test_user.username,
        "password": "test123"
    })
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试：查询KPI汇总，应只包含门店A的数据
    response = await async_client.get("/api/v1/kpi/summary", headers=headers)
    assert response.status_code == 200
    data = response.json()["data"]
    # 验证只统计了一个门店
    assert data["store_count"] == 1
    
    # 测试：查询门店B的KPI，应返回403
    response_b = await async_client.get(f"/api/v1/kpi/summary?store_id={store_b.id}", headers=headers)
    assert response_b.status_code == 403


@pytest.mark.asyncio
async def test_user_store_management_api(async_client: AsyncClient, db_session, test_admin, test_user):
    """测试：用户门店权限管理API"""
    # 创建门店
    stores = [
        Store(code=f"USM_{i}", name=f"门店{i}", address=f"地址{i}", is_active=True)
        for i in range(1, 4)
    ]
    db_session.add_all(stores)
    await db_session.commit()
    for store in stores:
        await db_session.refresh(store)
    
    # 登录admin
    login_response = await async_client.post("/api/v1/auth/login", json={
        "username": test_admin.username,
        "password": "admin123"
    })
    token = login_response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试1：分配门店权限
    response = await async_client.post(
        "/api/v1/user-stores/assign",
        json={
            "user_id": test_user.id,
            "store_ids": [stores[0].id, stores[1].id]
        },
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_stores"] == 2
    
    # 测试2：查询用户的门店权限
    response = await async_client.get(
        f"/api/v1/user-stores?user_id={test_user.id}",
        headers=headers
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 2
    assert len(data["stores"]) == 2
    
    # 测试3：更新门店权限（覆盖式）
    response = await async_client.post(
        "/api/v1/user-stores/assign",
        json={
            "user_id": test_user.id,
            "store_ids": [stores[2].id]  # 只保留第三个门店
        },
        headers=headers
    )
    assert response.status_code == 200
    
    # 验证更新后的权限
    response = await async_client.get(
        f"/api/v1/user-stores?user_id={test_user.id}",
        headers=headers
    )
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["stores"][0]["store_id"] == stores[2].id
    
    # 测试4：删除所有门店权限
    response = await async_client.delete(
        f"/api/v1/user-stores?user_id={test_user.id}",
        headers=headers
    )
    assert response.status_code == 200
    
    # 验证删除后无权限
    response = await async_client.get(
        f"/api/v1/user-stores?user_id={test_user.id}",
        headers=headers
    )
    data = response.json()["data"]
    assert data["total"] == 0
