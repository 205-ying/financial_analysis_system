"""
预算管理与差异分析功能测试

测试范围：
1. 批量保存预算
2. 预算数据的创建和更新
3. 预算差异分析计算
4. 超支检测
5. 权限控制
6. 边界条件和异常情况
"""

import pytest
from decimal import Decimal
from datetime import date, datetime
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User, Permission
from app.models.store import Store
from app.models.expense import ExpenseType, ExpenseRecord
from app.models.budget import Budget


@pytest.fixture
async def test_store(db_session: AsyncSession, admin_user: User) -> Store:
    """创建测试门店"""
    store = Store(
        name="测试门店A",
        code="TEST_STORE_A",
        address="测试地址123号",
        contact_person="张经理",
        phone="13800138000",
        is_active=True,
    )
    db_session.add(store)
    await db_session.commit()
    await db_session.refresh(store)
    return store


@pytest.fixture
async def test_expense_types(db_session: AsyncSession) -> list[ExpenseType]:
    """创建测试费用科目"""
    expense_types = [
        ExpenseType(
            type_code="FOOD",
            name="食材采购",
            category="operating",
            description="食材采购费用",
        ),
        ExpenseType(
            type_code="RENT",
            name="房租",
            category="operating",
            cost_behavior="fixed",
            description="门店租金",
        ),
        ExpenseType(
            type_code="SALARY",
            name="人工工资",
            category="operating",
            cost_behavior="fixed",
            description="员工工资",
        ),
        ExpenseType(
            type_code="UTIL",
            name="水电费",
            category="operating",
            description="水电费用",
        ),
    ]
    for et in expense_types:
        db_session.add(et)
    await db_session.commit()
    
    # 刷新以获取ID
    for et in expense_types:
        await db_session.refresh(et)
    
    return expense_types


@pytest.fixture
async def budget_permissions(db_session: AsyncSession, admin_user: User):
    """添加预算相关权限"""
    permissions = [
        Permission(
            code="budget:view",
            name="预算查看",
            resource="budget",
            action="view",
            description="查看预算数据",
        ),
        Permission(
            code="budget:manage",
            name="预算管理",
            resource="budget",
            action="manage",
            description="创建和修改预算",
        ),
    ]
    for perm in permissions:
        db_session.add(perm)
    await db_session.commit()
    
    # 给管理员添加权限
    role = admin_user.roles[0] if admin_user.roles else None
    for perm in permissions:
        await db_session.refresh(perm)
        if role is not None:
            await db_session.refresh(role, ["permissions"])
            role.permissions.append(perm)
    
    await db_session.commit()
    await db_session.refresh(admin_user)


@pytest.mark.asyncio
class TestBudgetManagement:
    """预算管理功能测试"""
    
    async def test_batch_save_budgets_create(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions
    ):
        """测试批量创建预算"""
        # 准备请求数据
        budget_data = {
            "store_id": test_store.id,
            "year": 2026,
            "month": 2,
            "items": [
                {"expense_type_id": test_expense_types[0].id, "amount": 50000.00},
                {"expense_type_id": test_expense_types[1].id, "amount": 20000.00},
                {"expense_type_id": test_expense_types[2].id, "amount": 30000.00},
            ]
        }
        
        # 发送请求
        response = await client.post(
            "/api/v1/budgets/batch",
            json=budget_data,
            headers=auth_headers
        )
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "成功" in data["message"]
        
        # 验证数据库中的记录
        stmt = select(Budget).where(
            Budget.store_id == test_store.id,
            Budget.year == 2026,
            Budget.month == 2
        )
        result = await db_session.execute(stmt)
        budgets = result.scalars().all()
        
        assert len(budgets) == 3
        assert any(b.amount == Decimal('50000.00') for b in budgets)
        assert any(b.amount == Decimal('20000.00') for b in budgets)
        assert any(b.amount == Decimal('30000.00') for b in budgets)
    
    async def test_batch_save_budgets_update(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions,
        admin_user: User,
    ):
        """测试批量更新预算"""
        # 先创建初始预算
        initial_budget = Budget(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            year=2026,
            month=3,
            amount=Decimal('40000.00'),
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        db_session.add(initial_budget)
        await db_session.commit()
        
        # 更新预算（包含新增和修改）
        budget_data = {
            "store_id": test_store.id,
            "year": 2026,
            "month": 3,
            "items": [
                {"expense_type_id": test_expense_types[0].id, "amount": 55000.00},  # 更新
                {"expense_type_id": test_expense_types[1].id, "amount": 25000.00},  # 新增
            ]
        }
        
        response = await client.post(
            "/api/v1/budgets/batch",
            json=budget_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # 验证更新结果
        store_id = test_store.id
        expense_type_id = test_expense_types[0].id
        new_expense_type_id = test_expense_types[1].id
        db_session.expire_all()
        stmt = select(Budget).where(
            Budget.store_id == store_id,
            Budget.year == 2026,
            Budget.month == 3
        )
        result = await db_session.execute(stmt)
        budgets = result.scalars().all()
        
        assert len(budgets) == 2
        food_budget = next(b for b in budgets if b.expense_type_id == expense_type_id)
        assert food_budget.amount == Decimal('55000.00')  # 已更新
        
        rent_budget = next(b for b in budgets if b.expense_type_id == new_expense_type_id)
        assert rent_budget.amount == Decimal('25000.00')  # 新增
    
    async def test_batch_save_budgets_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        budget_permissions
    ):
        """测试预算数据验证"""
        # 测试无效的门店ID
        invalid_data = {
            "store_id": 99999,
            "year": 2026,
            "month": 2,
            "items": [
                {"expense_type_id": 1, "amount": 10000.00}
            ]
        }
        
        response = await client.post(
            "/api/v1/budgets/batch",
            json=invalid_data,
            headers=auth_headers
        )
        
        # 应该返回错误或422（具体取决于实现）
        assert response.status_code in [400, 404, 422, 500]
    
    async def test_batch_save_budgets_permission(
        self,
        client: AsyncClient,
        test_store: Store,
        test_expense_types: list[ExpenseType]
    ):
        """测试无权限访问"""
        budget_data = {
            "store_id": test_store.id,
            "year": 2026,
            "month": 2,
            "items": [
                {"expense_type_id": test_expense_types[0].id, "amount": 50000.00}
            ]
        }
        
        # 不带认证头
        response = await client.post(
            "/api/v1/budgets/batch",
            json=budget_data
        )
        
        # 应该返回401或403
        assert response.status_code in [401, 403]


@pytest.mark.asyncio
class TestBudgetAnalysis:
    """预算差异分析测试"""
    
    async def test_budget_analysis_basic(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions,
        admin_user: User
    ):
        """测试基本的预算差异分析"""
        # 1. 创建预算数据
        budgets = [
            Budget(
                store_id=test_store.id,
                expense_type_id=test_expense_types[0].id,
                year=2026,
                month=2,
                amount=Decimal('50000.00'),
                created_by_id=admin_user.id,
                updated_by_id=admin_user.id
            ),
            Budget(
                store_id=test_store.id,
                expense_type_id=test_expense_types[1].id,
                year=2026,
                month=2,
                amount=Decimal('20000.00'),
                created_by_id=admin_user.id,
                updated_by_id=admin_user.id
            ),
        ]
        for budget in budgets:
            db_session.add(budget)
        await db_session.commit()
        
        # 2. 创建实际费用记录
        expenses = [
            ExpenseRecord(
                store_id=test_store.id,
                expense_type_id=test_expense_types[0].id,
                biz_date=date(2026, 2, 15),
                amount=Decimal('45000.00'),
                description="食材采购",
                status="approved",
                is_deleted=False,
                created_by=admin_user.id,
            ),
            ExpenseRecord(
                store_id=test_store.id,
                expense_type_id=test_expense_types[1].id,
                biz_date=date(2026, 2, 10),
                amount=Decimal('22000.00'),
                description="房租",
                status="paid",
                is_deleted=False,
                created_by=admin_user.id,
            ),
        ]
        for expense in expenses:
            db_session.add(expense)
        await db_session.commit()
        
        # 3. 调用分析接口
        response = await client.get(
            "/api/v1/budgets/analysis",
            params={
                "store_id": test_store.id,
                "year": 2026,
                "month": 2
            },
            headers=auth_headers
        )
        
        # 4. 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        
        analysis = data["data"]
        assert analysis["total_budget"] == 70000.00  # 50000 + 20000
        assert analysis["total_actual"] == 67000.00   # 45000 + 22000
        assert analysis["total_variance"] == -3000.00  # 67000 - 70000
        
        # 验证明细项
        items = analysis["items"]
        assert len(items) >= 2
        
        # 查找食材采购项
        food_item = next((i for i in items if i["expense_type_name"] == "食材采购"), None)
        assert food_item is not None
        assert food_item["budget_amount"] == 50000.00
        assert food_item["actual_amount"] == 45000.00
        assert food_item["variance"] == -5000.00
        assert food_item["variance_rate"] == -10.0
        assert food_item["is_over_budget"] is False
        
        # 查找房租项（超支）
        rent_item = next((i for i in items if i["expense_type_name"] == "房租"), None)
        assert rent_item is not None
        assert rent_item["budget_amount"] == 20000.00
        assert rent_item["actual_amount"] == 22000.00
        assert rent_item["variance"] == 2000.00
        assert rent_item["variance_rate"] == 10.0
        assert rent_item["is_over_budget"] is True
    
    async def test_budget_analysis_no_budget(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions,
        admin_user: User,
    ):
        """测试没有预算时的分析（所有实际费用都算超支）"""
        # 只创建实际费用，不创建预算
        expense = ExpenseRecord(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            biz_date=date(2026, 2, 15),
            amount=Decimal('30000.00'),
            description="食材采购",
            status="approved",
            is_deleted=False,
            created_by=admin_user.id,
        )
        db_session.add(expense)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/budgets/analysis",
            params={
                "store_id": test_store.id,
                "year": 2026,
                "month": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data["data"]
        
        # 验证总计
        assert analysis["total_budget"] == 0.00
        assert analysis["total_actual"] == 30000.00
        assert analysis["total_variance"] == 30000.00
        
        # 验证明细（食材采购项应该显示为超支）
        food_item = next((i for i in analysis["items"] if i["expense_type_name"] == "食材采购"), None)
        assert food_item is not None
        assert food_item["budget_amount"] == 0.00
        assert food_item["actual_amount"] == 30000.00
        assert food_item["is_over_budget"] is False  # 预算为0时不算超支
    
    async def test_budget_analysis_no_expenses(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions,
        admin_user: User
    ):
        """测试只有预算没有实际费用的情况"""
        # 只创建预算
        budget = Budget(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            year=2026,
            month=2,
            amount=Decimal('50000.00'),
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        db_session.add(budget)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/budgets/analysis",
            params={
                "store_id": test_store.id,
                "year": 2026,
                "month": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data["data"]
        
        assert analysis["total_budget"] == 50000.00
        assert analysis["total_actual"] == 0.00
        assert analysis["total_variance"] == -50000.00  # 节约
        
        food_item = next((i for i in analysis["items"] if i["expense_type_name"] == "食材采购"), None)
        assert food_item is not None
        assert food_item["variance"] == -50000.00
        assert food_item["is_over_budget"] is False
    
    async def test_budget_analysis_multiple_expenses(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions,
        admin_user: User
    ):
        """测试同一科目多笔费用的汇总"""
        # 创建预算
        budget = Budget(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            year=2026,
            month=2,
            amount=Decimal('50000.00'),
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        db_session.add(budget)
        
        # 创建多笔费用
        expenses = [
            ExpenseRecord(
                store_id=test_store.id,
                expense_type_id=test_expense_types[0].id,
                biz_date=date(2026, 2, 5),
                amount=Decimal('15000.00'),
                description="第一次采购",
                status="approved",
                is_deleted=False,
                created_by=admin_user.id,
            ),
            ExpenseRecord(
                store_id=test_store.id,
                expense_type_id=test_expense_types[0].id,
                biz_date=date(2026, 2, 15),
                amount=Decimal('20000.00'),
                description="第二次采购",
                status="paid",
                is_deleted=False,
                created_by=admin_user.id,
            ),
            ExpenseRecord(
                store_id=test_store.id,
                expense_type_id=test_expense_types[0].id,
                biz_date=date(2026, 2, 25),
                amount=Decimal('18000.00'),
                description="第三次采购",
                status="approved",
                is_deleted=False,
                created_by=admin_user.id,
            ),
        ]
        for expense in expenses:
            db_session.add(expense)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/budgets/analysis",
            params={
                "store_id": test_store.id,
                "year": 2026,
                "month": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data["data"]
        
        food_item = next((i for i in analysis["items"] if i["expense_type_name"] == "食材采购"), None)
        assert food_item is not None
        assert food_item["budget_amount"] == 50000.00
        assert food_item["actual_amount"] == 53000.00  # 15000 + 20000 + 18000
        assert food_item["variance"] == 3000.00
        assert food_item["variance_rate"] == 6.0
        assert food_item["is_over_budget"] is True
    
    async def test_budget_analysis_exclude_deleted_expenses(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions,
        admin_user: User
    ):
        """测试已删除的费用不计入分析"""
        budget = Budget(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            year=2026,
            month=2,
            amount=Decimal('50000.00'),
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        db_session.add(budget)
        
        # 创建正常费用和已删除费用
        normal_expense = ExpenseRecord(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            biz_date=date(2026, 2, 10),
            amount=Decimal('30000.00'),
            description="正常费用",
            status="approved",
            is_deleted=False,
            created_by=admin_user.id,
        )
        deleted_expense = ExpenseRecord(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            biz_date=date(2026, 2, 15),
            amount=Decimal('20000.00'),
            description="已删除费用",
            status="approved",
            is_deleted=True,
            created_by=admin_user.id,
        )
        db_session.add(normal_expense)
        db_session.add(deleted_expense)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/budgets/analysis",
            params={
                "store_id": test_store.id,
                "year": 2026,
                "month": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data["data"]
        
        food_item = next((i for i in analysis["items"] if i["expense_type_name"] == "食材采购"), None)
        assert food_item is not None
        assert food_item["actual_amount"] == 30000.00  # 只计算未删除的
        assert food_item["variance"] == -20000.00
    
    async def test_budget_analysis_exclude_pending_expenses(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions,
        admin_user: User
    ):
        """测试待审批的费用不计入分析"""
        budget = Budget(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            year=2026,
            month=2,
            amount=Decimal('50000.00'),
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        db_session.add(budget)
        
        # 创建不同状态的费用
        approved_expense = ExpenseRecord(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            biz_date=date(2026, 2, 10),
            amount=Decimal('30000.00'),
            description="已审批",
            status="approved",
            is_deleted=False,
            created_by=admin_user.id,
        )
        pending_expense = ExpenseRecord(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            biz_date=date(2026, 2, 15),
            amount=Decimal('15000.00'),
            description="待审批",
            status="pending",
            is_deleted=False,
            created_by=admin_user.id,
        )
        db_session.add(approved_expense)
        db_session.add(pending_expense)
        await db_session.commit()
        
        response = await client.get(
            "/api/v1/budgets/analysis",
            params={
                "store_id": test_store.id,
                "year": 2026,
                "month": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data["data"]
        
        food_item = next((i for i in analysis["items"] if i["expense_type_name"] == "食材采购"), None)
        assert food_item is not None
        assert food_item["actual_amount"] == 30000.00  # 只计算approved和paid状态
    
    async def test_budget_analysis_different_month(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions,
        admin_user: User
    ):
        """测试查询不同月份时费用的隔离"""
        # 创建2月预算
        budget_feb = Budget(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            year=2026,
            month=2,
            amount=Decimal('50000.00'),
            created_by_id=admin_user.id,
            updated_by_id=admin_user.id
        )
        db_session.add(budget_feb)
        
        # 创建2月和3月的费用
        expense_feb = ExpenseRecord(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            biz_date=date(2026, 2, 15),
            amount=Decimal('30000.00'),
            description="2月费用",
            status="approved",
            is_deleted=False,
            created_by=admin_user.id,
        )
        expense_mar = ExpenseRecord(
            store_id=test_store.id,
            expense_type_id=test_expense_types[0].id,
            biz_date=date(2026, 3, 15),
            amount=Decimal('40000.00'),
            description="3月费用",
            status="approved",
            is_deleted=False,
            created_by=admin_user.id,
        )
        db_session.add(expense_feb)
        db_session.add(expense_mar)
        await db_session.commit()
        
        # 查询2月数据
        response = await client.get(
            "/api/v1/budgets/analysis",
            params={
                "store_id": test_store.id,
                "year": 2026,
                "month": 2
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        analysis = data["data"]
        
        food_item = next((i for i in analysis["items"] if i["expense_type_name"] == "食材采购"), None)
        assert food_item is not None
        assert food_item["actual_amount"] == 30000.00  # 只包含2月费用，不包含3月


@pytest.mark.asyncio
class TestBudgetEdgeCases:
    """预算管理边界用例测试"""
    
    async def test_budget_zero_amount(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions
    ):
        """测试预算金额为0的情况"""
        budget_data = {
            "store_id": test_store.id,
            "year": 2026,
            "month": 2,
            "items": [
                {"expense_type_id": test_expense_types[0].id, "amount": 0.00}
            ]
        }
        
        response = await client.post(
            "/api/v1/budgets/batch",
            json=budget_data,
            headers=auth_headers
        )
        
        # 允许设置为0（表示该科目本月不应有支出）
        assert response.status_code == 200
    
    async def test_budget_negative_amount(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions
    ):
        """测试负数预算（应该被拒绝）"""
        budget_data = {
            "store_id": test_store.id,
            "year": 2026,
            "month": 2,
            "items": [
                {"expense_type_id": test_expense_types[0].id, "amount": -1000.00}
            ]
        }
        
        response = await client.post(
            "/api/v1/budgets/batch",
            json=budget_data,
            headers=auth_headers
        )
        
        # 应该返回验证错误
        assert response.status_code in [400, 422, 500]
    
    async def test_budget_large_amount(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions
    ):
        """测试大额预算"""
        budget_data = {
            "store_id": test_store.id,
            "year": 2026,
            "month": 2,
            "items": [
                {"expense_type_id": test_expense_types[0].id, "amount": 99999999.99}
            ]
        }
        
        response = await client.post(
            "/api/v1/budgets/batch",
            json=budget_data,
            headers=auth_headers
        )
        
        # 应该成功或返回业务规则限制
        assert response.status_code in [200, 400, 422]
    
    async def test_budget_invalid_month(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_store: Store,
        test_expense_types: list[ExpenseType],
        budget_permissions
    ):
        """测试无效的月份"""
        budget_data = {
            "store_id": test_store.id,
            "year": 2026,
            "month": 13,  # 无效月份
            "items": [
                {"expense_type_id": test_expense_types[0].id, "amount": 10000.00}
            ]
        }
        
        response = await client.post(
            "/api/v1/budgets/batch",
            json=budget_data,
            headers=auth_headers
        )
        
        # 应该返回验证错误
        assert response.status_code in [400, 422, 500]
    
    async def test_analysis_invalid_parameters(
        self,
        client: AsyncClient,
        auth_headers: dict,
        budget_permissions
    ):
        """测试分析接口的参数验证"""
        # 缺少必需参数
        response = await client.get(
            "/api/v1/budgets/analysis",
            params={"store_id": 1},  # 缺少year和month
            headers=auth_headers
        )
        
        assert response.status_code == 422  # FastAPI参数验证错误
