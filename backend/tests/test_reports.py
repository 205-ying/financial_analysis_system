"""
报表中心模块测试
"""
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from httpx import AsyncClient

from app.models.kpi import KpiDailyStore
from app.models.order import OrderHeader
from app.models.expense import ExpenseRecord


class TestReportsAPI:
    """报表API测试"""
    
    @pytest.mark.asyncio
    async def test_daily_summary_success(
        self,
        client: AsyncClient,
        admin_headers: dict,
        test_store,
        db_session
    ):
        """测试日汇总报表 - 成功"""
        # 准备测试数据 - 创建 KPI 记录
        today = date.today()
        kpi_data = KpiDailyStore(
            biz_date=today,
            store_id=test_store.id,
            revenue=Decimal("10000.00"),
            net_revenue=Decimal("9500.00"),
            discount_amount=Decimal("500.00"),
            refund_amount=Decimal("0.00"),
            cost_total=Decimal("3000.00"),
            cost_material=Decimal("2000.00"),
            cost_labor=Decimal("1000.00"),
            gross_profit=Decimal("7000.00"),
            operating_profit=Decimal("6500.00")
        )
        db_session.add(kpi_data)
        await db_session.commit()
        
        # 请求报表
        response = await client.get(
            "/api/v1/reports/daily-summary",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat(),
                "store_id": test_store.id
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert isinstance(result["data"], list)
        
        # 验证数据字段
        if len(result["data"]) > 0:
            item = result["data"][0]
            assert "biz_date" in item
            assert "store_id" in item
            assert "store_name" in item
            assert "revenue" in item
            assert "net_revenue" in item
            assert "cost_total" in item
            assert "gross_profit" in item
            assert "operating_profit" in item
            assert "gross_profit_rate" in item
            assert "operating_profit_rate" in item
    
    @pytest.mark.asyncio
    async def test_daily_summary_no_permission(
        self,
        client: AsyncClient,
        test_store
    ):
        """测试日汇总报表 - 无权限"""
        today = date.today()
        
        response = await client.get(
            "/api/v1/reports/daily-summary",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat()
            }
        )
        
        # 当前项目未登录统一返回 403
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_monthly_summary_success(
        self,
        client: AsyncClient,
        admin_headers: dict,
        test_store
    ):
        """测试月汇总报表 - 成功"""
        today = date.today()
        start_date = today.replace(day=1)
        
        response = await client.get(
            "/api/v1/reports/monthly-summary",
            params={
                "start_date": start_date.isoformat(),
                "end_date": today.isoformat(),
                "store_id": test_store.id
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert isinstance(result["data"], list)
    
    @pytest.mark.asyncio
    async def test_store_performance_success(
        self,
        client: AsyncClient,
        admin_headers: dict,
        test_store,
        db_session
    ):
        """测试门店绩效报表 - 成功"""
        # 准备测试数据
        today = date.today()
        kpi_data = KpiDailyStore(
            biz_date=today,
            store_id=test_store.id,
            revenue=Decimal("5000.00"),
            net_revenue=Decimal("4800.00"),
            cost_total=Decimal("1500.00"),
            gross_profit=Decimal("3500.00"),
            operating_profit=Decimal("3300.00")
        )
        db_session.add(kpi_data)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/reports/store-performance",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat()
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert isinstance(result["data"], list)
        
        # 验证字段
        if len(result["data"]) > 0:
            item = result["data"][0]
            assert "store_id" in item
            assert "store_name" in item
            assert "revenue" in item
            assert "order_count" in item
            assert "gross_profit" in item
            assert "revenue_rank" in item
            assert "profit_rank" in item
    
    @pytest.mark.asyncio
    async def test_store_performance_top_n(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """测试门店绩效报表 - TOP N"""
        today = date.today()
        
        response = await client.get(
            "/api/v1/reports/store-performance",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat(),
                "top_n": 5
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        # TOP N 限制应生效
        assert len(result["data"]) <= 5
    
    @pytest.mark.asyncio
    async def test_expense_breakdown_success(
        self,
        client: AsyncClient,
        admin_headers: dict,
        test_store,
        test_expense_type,
        admin_user,
        db_session
    ):
        """测试费用明细报表 - 成功"""
        # 准备测试数据 - 创建费用记录
        today = date.today()
        expense = ExpenseRecord(
            store_id=test_store.id,
            expense_type_id=test_expense_type.id,
            biz_date=today,
            amount=Decimal("1000.00"),
            description="测试费用",
            created_by=admin_user.id
        )
        db_session.add(expense)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/reports/expense-breakdown",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat(),
                "store_id": test_store.id
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 200
        assert isinstance(result["data"], list)
        
        # 验证字段
        if len(result["data"]) > 0:
            item = result["data"][0]
            assert "expense_type_id" in item
            assert "expense_type_code" in item
            assert "expense_type_name" in item
            assert "category" in item
            assert "total_amount" in item
            assert "record_count" in item
            assert "percentage" in item
    
    @pytest.mark.asyncio
    async def test_export_excel_success(
        self,
        client: AsyncClient,
        admin_headers: dict,
        test_store,
        db_session
    ):
        """测试导出 Excel - 成功"""
        # 准备测试数据
        today = date.today()
        kpi_data = KpiDailyStore(
            biz_date=today,
            store_id=test_store.id,
            revenue=Decimal("8000.00"),
            net_revenue=Decimal("7600.00"),
            cost_total=Decimal("2400.00"),
            gross_profit=Decimal("5600.00"),
            operating_profit=Decimal("5200.00")
        )
        db_session.add(kpi_data)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/reports/export",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat(),
                "store_id": test_store.id
            },
            headers=admin_headers
        )
        
        assert response.status_code == 200
        
        # 验证响应类型是 Excel
        content_type = response.headers.get("content-type")
        assert "spreadsheet" in content_type or "excel" in content_type
        
        # 验证有内容
        content = response.content
        assert len(content) > 0
        
        # 验证文件名
        content_disposition = response.headers.get("content-disposition")
        assert "attachment" in content_disposition
        assert ".xlsx" in content_disposition
    
    @pytest.mark.asyncio
    async def test_export_excel_no_permission(
        self,
        client: AsyncClient
    ):
        """测试导出 Excel - 无权限"""
        today = date.today()
        
        response = await client.get(
            "/api/v1/reports/export",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat()
            }
        )
        
        # 当前项目未登录统一返回 403
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_invalid_date_format(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """测试无效日期格式"""
        response = await client.get(
            "/api/v1/reports/daily-summary",
            params={
                "start_date": "invalid-date",
                "end_date": "2024-01-01"
            },
            headers=admin_headers
        )
        
        # 应该返回 400 或 422
        assert response.status_code in [400, 422]
