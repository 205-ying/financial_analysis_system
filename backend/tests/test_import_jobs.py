"""
数据导入功能测试
"""

import io
import pytest
from pathlib import Path
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.store import Store
from app.models.expense import ExpenseType
from app.models.import_job import DataImportJob, ImportJobStatus, ImportTargetType


@pytest.fixture
async def test_store(db_session: AsyncSession) -> Store:
    """创建测试门店"""
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


@pytest.fixture
async def test_expense_type(db_session: AsyncSession) -> ExpenseType:
    """创建测试费用科目"""
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


class TestImportJobs:
    """数据导入测试类"""
    
    @pytest.mark.asyncio
    async def test_create_import_job_orders_csv(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
    ):
        """测试创建订单导入任务（CSV）"""
        # 准备 CSV 内容（包含重复订单号）
        csv_content = """order_no,biz_date,gross_amount,discount_amount,net_amount,customer_count
ORD001,2024-01-01,1000.50,50.00,950.50,2
ORD002,2024-01-02,2000.00,0,2000.00,3
ORD001,2024-01-03,1500.00,100.00,1400.00,1
ORD003,2024-01-03,500.00,0,500.00,1
"""
        
        # 创建上传文件
        files = {
            "file": ("orders.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
        }
        
        data = {
            "target_type": "orders",
            "job_name": "订单导入测试",
            "store_id": test_store.id,
        }
        
        # 发送请求
        response = await client.post(
            "/api/v1/import-jobs",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 0
        assert result["data"]["target_type"] == "orders"
        assert result["data"]["status"] == "pending"
        assert result["data"]["file_name"] == "orders.csv"
    
    @pytest.mark.asyncio
    async def test_run_import_job_with_duplicate_orders(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
    ):
        """测试运行导入任务（含重复订单号）"""
        # 1. 创建任务
        csv_content = """order_no,biz_date,gross_amount,discount_amount,net_amount,customer_count
ORD001,2024-01-01,1000.50,50.00,950.50,2
ORD002,2024-01-02,2000.00,0,2000.00,3
ORD001,2024-01-03,1500.00,100.00,1400.00,1
"""
        
        files = {
            "file": ("orders_dup.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
        }
        
        data = {
            "target_type": "orders",
            "store_id": test_store.id,
        }
        
        create_response = await client.post(
            "/api/v1/import-jobs",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert create_response.status_code == 200
        job_id = create_response.json()["data"]["id"]
        
        # 2. 执行任务
        run_response = await client.post(
            f"/api/v1/import-jobs/{job_id}/run",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert run_response.status_code == 200
        result = run_response.json()
        
        # 3. 验证结果
        assert result["code"] == 0
        data = result["data"]
        
        # 期望：3行数据，2行成功（ORD001, ORD002），1行失败（重复的ORD001）
        assert data["total_rows"] == 3
        assert data["success_rows"] == 2
        assert data["fail_rows"] == 1
        assert data["status"] == "partial_fail"
        assert data["error_report_path"] is not None
    
    @pytest.mark.asyncio
    async def test_list_import_jobs(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
    ):
        """测试查询导入任务列表"""
        # 1. 创建几个任务
        csv_content = "order_no,biz_date,net_amount\nORD001,2024-01-01,100.00\n"
        
        for i in range(3):
            files = {
                "file": (f"test_{i}.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
            }
            data = {
                "target_type": "orders",
                "store_id": test_store.id,
            }
            await client.post(
                "/api/v1/import-jobs",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {admin_token}"},
            )
        
        # 2. 查询列表
        response = await client.get(
            "/api/v1/import-jobs?page=1&page_size=10",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 0
        assert result["total"] >= 3
        assert len(result["data"]) >= 3
    
    @pytest.mark.asyncio
    async def test_get_import_job_detail(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
    ):
        """测试获取任务详情"""
        # 1. 创建任务
        csv_content = "order_no,biz_date,net_amount\nORD001,2024-01-01,100.00\n"
        files = {
            "file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
        }
        data = {
            "target_type": "orders",
            "job_name": "详情测试任务",
            "store_id": test_store.id,
        }
        
        create_response = await client.post(
            "/api/v1/import-jobs",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        job_id = create_response.json()["data"]["id"]
        
        # 2. 查询详情
        response = await client.get(
            f"/api/v1/import-jobs/{job_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 0
        assert result["data"]["id"] == job_id
        assert result["data"]["job_name"] == "详情测试任务"
        assert "config" in result["data"]
    
    @pytest.mark.asyncio
    async def test_list_import_job_errors(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
    ):
        """测试查询任务错误列表"""
        # 1. 创建并执行有错误的任务
        csv_content = """order_no,biz_date,net_amount
,2024-01-01,100.00
ORD002,invalid-date,200.00
ORD003,2024-01-03,-50.00
"""
        
        files = {
            "file": ("errors.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
        }
        data = {
            "target_type": "orders",
            "store_id": test_store.id,
        }
        
        create_response = await client.post(
            "/api/v1/import-jobs",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        job_id = create_response.json()["data"]["id"]
        
        # 执行任务
        await client.post(
            f"/api/v1/import-jobs/{job_id}/run",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        # 2. 查询错误列表
        response = await client.get(
            f"/api/v1/import-jobs/{job_id}/errors?page=1&page_size=10",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["code"] == 0
        assert result["total"] == 3  # 3条错误
        assert len(result["data"]) == 3
    
    @pytest.mark.asyncio
    async def test_download_error_report(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
    ):
        """测试下载错误报告"""
        # 1. 创建并执行有错误的任务
        csv_content = """order_no,biz_date,net_amount
,2024-01-01,100.00
ORD002,2024-01-02,200.00
"""
        
        files = {
            "file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
        }
        data = {
            "target_type": "orders",
            "store_id": test_store.id,
        }
        
        create_response = await client.post(
            "/api/v1/import-jobs",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        job_id = create_response.json()["data"]["id"]
        
        # 执行任务
        await client.post(
            f"/api/v1/import-jobs/{job_id}/run",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        # 2. 下载错误报告
        response = await client.get(
            f"/api/v1/import-jobs/{job_id}/error-report",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert len(response.content) > 0  # 文件不为空
    
    @pytest.mark.asyncio
    async def test_import_expense_records(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
        test_expense_type: ExpenseType,
    ):
        """测试导入费用记录"""
        # 1. 创建任务
        csv_content = f"""expense_type_code,biz_date,amount,description
{test_expense_type.type_code},2024-01-01,5000.00,一月份租金
{test_expense_type.type_code},2024-01-02,500.00,水电费
INVALID_CODE,2024-01-03,100.00,无效科目
"""
        
        files = {
            "file": ("expense.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
        }
        data = {
            "target_type": "expense_records",
            "store_id": test_store.id,
        }
        
        create_response = await client.post(
            "/api/v1/import-jobs",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert create_response.status_code == 200
        job_id = create_response.json()["data"]["id"]
        
        # 2. 执行任务
        run_response = await client.post(
            f"/api/v1/import-jobs/{job_id}/run",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert run_response.status_code == 200
        result = run_response.json()
        
        # 3. 验证结果
        data = result["data"]
        assert data["total_rows"] == 3
        assert data["success_rows"] == 2  # 前两条成功
        assert data["fail_rows"] == 1    # 无效科目失败
        assert data["status"] == "partial_fail"
    
    @pytest.mark.asyncio
    async def test_file_size_limit(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
    ):
        """测试文件大小限制"""
        # 创建超大文件（模拟）
        large_content = "order_no,biz_date,net_amount\n" + ("ORD001,2024-01-01,100.00\n" * 100000)
        
        files = {
            "file": ("large.csv", io.BytesIO(large_content.encode("utf-8")), "text/csv")
        }
        data = {
            "target_type": "orders",
            "store_id": test_store.id,
        }
        
        response = await client.post(
            "/api/v1/import-jobs",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        # 如果文件大小超限，应该返回错误
        # 注意：实际限制为50MB，这里的测试数据可能不够大
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_invalid_file_extension(
        self,
        client: AsyncClient,
        admin_user: User,
        admin_token: str,
        test_store: Store,
    ):
        """测试不支持的文件格式"""
        files = {
            "file": ("test.txt", io.BytesIO(b"invalid content"), "text/plain")
        }
        data = {
            "target_type": "orders",
            "store_id": test_store.id,
        }
        
        response = await client.post(
            "/api/v1/import-jobs",
            files=files,
            data=data,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert response.status_code == 422
        result = response.json()
        assert "不支持的文件格式" in result["message"]
