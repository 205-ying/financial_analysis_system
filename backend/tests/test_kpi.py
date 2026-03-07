from datetime import date, timedelta
from datetime import datetime

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import ExpenseRecord, ExpenseType
from app.models.order import OrderHeader
from app.models.store import Store
from app.models.user import User


@pytest.mark.asyncio
class TestKPI:
    """KPI相关测试"""
    
    @pytest.fixture(autouse=True)
    async def setup_test_data(self, db_session: AsyncSession, admin_user: User):
        """为每个测试准备测试数据"""
        # 创建测试门店
        store = Store(
            code="TEST001",
            name="测试门店",
            address="测试地址",
            is_active=True,
        )
        db_session.add(store)
        await db_session.flush()
        
        # 创建测试订单
        today = date.today()
        order = OrderHeader(
            order_no=f"ORD{today.strftime('%Y%m%d')}001",
            store_id=store.id,
            biz_date=today,
            order_time=datetime.combine(today, datetime.min.time()),
            channel="dine_in",
            gross_amount=1000.00,
            discount_amount=50.00,
            net_amount=950.00,
            service_charge=0.00,
            delivery_fee=0.00,
            payment_method="cash",
            status="completed",
        )
        db_session.add(order)
        
        # 创建费用类型
        expense_type = ExpenseType(
            type_code="MATERIAL",
            name="原材料",
            category="operating",
            cost_behavior="variable",
            description="食材成本",
        )
        db_session.add(expense_type)
        await db_session.flush()
        
        # 创建费用记录
        expense = ExpenseRecord(
            store_id=store.id,
            expense_type_id=expense_type.id,
            biz_date=today,
            amount=300.00,
            description="测试费用",
            created_by=admin_user.id,
            status="approved",
        )
        db_session.add(expense)
        
        await db_session.commit()
        
        # 保存ID供测试使用
        self.store_id = store.id
        self.today = today
    
    async def test_rebuild_kpi_success(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """测试KPI重建成功"""
        # 准备请求数据
        start_date = (self.today - timedelta(days=7)).isoformat()
        end_date = self.today.isoformat()
        
        response = await client.post(
            "/api/v1/kpi/rebuild",
            headers=auth_headers,
            json={
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total_records" in data["data"]
        assert data["data"]["total_records"] >= 0
    
    async def test_rebuild_kpi_with_store_id(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """测试指定门店的KPI重建"""
        start_date = self.today.isoformat()
        end_date = self.today.isoformat()
        
        response = await client.post(
            "/api/v1/kpi/rebuild",
            headers=auth_headers,
            json={
                "start_date": start_date,
                "end_date": end_date,
                "store_id": self.store_id
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["affected_stores"] == 1
    
    async def test_rebuild_kpi_invalid_date_range(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """测试无效的日期范围"""
        # 开始日期大于结束日期
        start_date = self.today.isoformat()
        end_date = (self.today - timedelta(days=7)).isoformat()
        
        response = await client.post(
            "/api/v1/kpi/rebuild",
            headers=auth_headers,
            json={
                "start_date": start_date,
                "end_date": end_date
            }
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "开始日期不能大于结束日期" in data["detail"]
    
    async def test_get_kpi_summary(
        self, 
        client: AsyncClient, 
        auth_headers: dict
    ):
        """测试获取KPI汇总"""
        response = await client.get(
            "/api/v1/kpi/summary",
            headers=auth_headers,
            params={
                "start_date": (self.today - timedelta(days=7)).isoformat(),
                "end_date": self.today.isoformat()
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total_revenue" in data["data"]
        assert "total_cost" in data["data"]
        assert "total_profit" in data["data"]
    
    async def test_rebuild_kpi_without_permission(
        self, 
        client: AsyncClient
    ):
        """测试没有权限时不能重建KPI"""
        response = await client.post(
            "/api/v1/kpi/rebuild",
            json={
                "start_date": "2026-01-01",
                "end_date": "2026-01-24"
            }
        )
        
        # 当前项目未登录统一返回 403
        assert response.status_code == 403
