"""
种子数据脚本：初始化基础数据

使用方法：
python backend/scripts/seed_data.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import date, datetime
from decimal import Decimal
import bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.user import User, Role, Permission, user_role, role_permission
from app.models.store import Store, ProductCategory, Product
from app.models.expense import ExpenseType
from app.models.user_store import UserStorePermission


def hash_password(password: str) -> str:
    """使用 bcrypt 加密密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


async def seed_users_and_permissions(session: AsyncSession):
    """初始化用户、角色和权限"""
    print("🔐 初始化用户、角色和权限...")
    
    # 检查是否已经初始化过
    result = await session.execute(select(Permission).limit(1))
    if result.scalar_one_or_none() is not None:
        print("  ⚠️  权限数据已存在，跳过初始化")
        return
    
    # 1. 创建权限
    permissions = [
        # 用户管理
        Permission(code="user:view", name="查看用户", resource="user", action="view", description="查看用户列表和详情"),
        Permission(code="user:create", name="创建用户", resource="user", action="create", description="创建新用户"),
        Permission(code="user:edit", name="编辑用户", resource="user", action="edit", description="编辑用户信息"),
        Permission(code="user:delete", name="删除用户", resource="user", action="delete", description="删除用户"),
        
        # 门店管理
        Permission(code="store:view", name="查看门店", resource="store", action="view", description="查看门店列表和详情"),
        Permission(code="store:create", name="创建门店", resource="store", action="create", description="创建新门店"),
        Permission(code="store:edit", name="编辑门店", resource="store", action="edit", description="编辑门店信息"),
        Permission(code="store:delete", name="删除门店", resource="store", action="delete", description="删除门店"),
        
        # 产品管理
        Permission(code="product:view", name="查看产品", resource="product", action="view", description="查看产品列表和详情"),
        Permission(code="product:create", name="创建产品", resource="product", action="create", description="创建新产品"),
        Permission(code="product:edit", name="编辑产品", resource="product", action="edit", description="编辑产品信息"),
        Permission(code="product:delete", name="删除产品", resource="product", action="delete", description="删除产品"),
        
        # 订单管理
        Permission(code="order:view", name="查看订单", resource="order", action="view", description="查看订单列表和详情"),
        Permission(code="order:create", name="创建订单", resource="order", action="create", description="创建新订单"),
        Permission(code="order:edit", name="编辑订单", resource="order", action="edit", description="编辑订单信息"),
        Permission(code="order:cancel", name="取消订单", resource="order", action="cancel", description="取消订单"),
        
        # 费用管理
        Permission(code="expense:view", name="查看费用", resource="expense", action="view", description="查看费用列表和详情"),
        Permission(code="expense:create", name="创建费用", resource="expense", action="create", description="创建新费用记录"),
        Permission(code="expense:edit", name="编辑费用", resource="expense", action="edit", description="编辑费用信息"),
        Permission(code="expense:approve", name="审批费用", resource="expense", action="approve", description="审批费用申请"),
        
        # KPI 查看
        Permission(code="kpi:view", name="查看 KPI", resource="kpi", action="view", description="查看 KPI 报表"),
        Permission(code="kpi:export", name="导出 KPI", resource="kpi", action="export", description="导出 KPI 数据"),
        
        # 数据导入
        Permission(code="import_job:create", name="创建导入任务", resource="import_job", action="create", description="上传文件创建导入任务"),
        Permission(code="import_job:run", name="执行导入任务", resource="import_job", action="run", description="执行数据导入"),
        Permission(code="import_job:view", name="查看导入任务", resource="import_job", action="view", description="查看导入任务列表和详情"),
        Permission(code="import_job:download", name="下载错误报告", resource="import_job", action="download", description="下载导入错误报告"),
        
        # 报表中心
        Permission(code="report:view", name="查看报表", resource="report", action="view", description="查看各类报表"),
        Permission(code="report:export", name="导出报表", resource="report", action="export", description="导出报表为Excel文件"),
        
        # 系统管理
        Permission(code="system:config", name="系统配置", resource="system", action="config", description="系统配置管理"),
        Permission(code="system:audit", name="审计日志", resource="system", action="audit", description="查看审计日志"),
        
        # 用户门店权限管理
        Permission(code="user:assign-store", name="分配门店权限", resource="user", action="assign-store", description="为用户分配门店数据权限"),
    ]
    session.add_all(permissions)
    await session.flush()  # 确保权限 ID 生成
    
    # 2. 创建角色
    role_admin = Role(
        code="admin",
        name="系统管理员",
        description="拥有系统所有权限",
        is_active=True
    )
    
    role_manager = Role(
        code="manager",
        name="门店经理",
        description="管理单个或多个门店的日常运营",
        is_active=True
    )
    
    role_cashier = Role(
        code="cashier",
        name="收银员",
        description="处理订单和收款",
        is_active=True
    )
    
    role_accountant = Role(
        code="accountant",
        name="财务人员",
        description="管理费用和查看财务报表",
        is_active=True
    )
    
    session.add_all([role_admin, role_manager, role_cashier, role_accountant])
    await session.flush()
    
    # 3. 分配权限给角色
    # 管理员拥有所有权限
    for perm in permissions:
        await session.execute(
            role_permission.insert().values(role_id=role_admin.id, permission_id=perm.id)
        )
    
    # 门店经理权限
    manager_perms = [p for p in permissions if p.code.startswith(("store:", "product:", "order:", "expense:view", "expense:create", "kpi:"))]
    for perm in manager_perms:
        await session.execute(
            role_permission.insert().values(role_id=role_manager.id, permission_id=perm.id)
        )
    
    # 收银员权限
    cashier_perms = [p for p in permissions if p.code.startswith(("order:view", "order:create", "product:view"))]
    for perm in cashier_perms:
        await session.execute(
            role_permission.insert().values(role_id=role_cashier.id, permission_id=perm.id)
        )
    
    # 财务人员权限
    accountant_perms = [p for p in permissions if p.code.startswith(("expense:", "kpi:"))]
    for perm in accountant_perms:
        await session.execute(
            role_permission.insert().values(role_id=role_accountant.id, permission_id=perm.id)
        )
    
    # 4. 创建用户
    user_admin = User(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("Admin@123"),
        full_name="系统管理员",
        phone="13800138000",
        is_active=True,
        is_superuser=True
    )
    
    user_manager = User(
        username="manager",
        email="manager@example.com",
        password_hash=hash_password("Manager@123"),
        full_name="张经理",
        phone="13800138001",
        is_active=True,
        is_superuser=False
    )
    
    user_cashier = User(
        username="cashier",
        email="cashier@example.com",
        password_hash=hash_password("Cashier@123"),
        full_name="李收银",
        phone="13800138002",
        is_active=True,
        is_superuser=False
    )
    
    session.add_all([user_admin, user_manager, user_cashier])
    await session.flush()
    
    # 5. 分配角色给用户
    await session.execute(user_role.insert().values(user_id=user_admin.id, role_id=role_admin.id))
    await session.execute(user_role.insert().values(user_id=user_manager.id, role_id=role_manager.id))
    await session.execute(user_role.insert().values(user_id=user_cashier.id, role_id=role_cashier.id))
    
    print(f"  ✅ 创建了 {len(permissions)} 个权限")
    print(f"  ✅ 创建了 4 个角色")
    print(f"  ✅ 创建了 3 个用户 (admin/Admin@123, manager/Manager@123, cashier/Cashier@123)")


async def seed_stores(session: AsyncSession):
    """初始化门店数据"""
    print("🏪 初始化门店数据...")
    
    # 检查是否已经初始化过
    result = await session.execute(select(Store).limit(1))
    if result.scalar_one_or_none() is not None:
        print("  ⚠️  门店数据已存在，跳过初始化")
        return
    
    stores = [
        Store(
            code="S001",
            name="中关村店",
            address="北京市海淀区中关村大街1号",
            phone="010-12345678",
            contact_person="王店长",
            business_hours="10:00-22:00",
            area_sqm=Decimal("150.00"),
            is_active=True,
            sort_order=1,
            remark="旗舰店"
        ),
        Store(
            code="S002",
            name="三里屯店",
            address="北京市朝阳区三里屯路11号",
            phone="010-87654321",
            contact_person="李店长",
            business_hours="10:00-23:00",
            area_sqm=Decimal("120.00"),
            is_active=True,
            sort_order=2,
            remark="商圈店"
        ),
        Store(
            code="S003",
            name="望京店",
            address="北京市朝阳区望京SOHO",
            phone="010-11112222",
            contact_person="赵店长",
            business_hours="09:00-21:00",
            area_sqm=Decimal("100.00"),
            is_active=True,
            sort_order=3,
            remark="社区店"
        ),
    ]
    
    session.add_all(stores)
    print(f"  ✅ 创建了 {len(stores)} 个门店")


async def seed_product_categories(session: AsyncSession):
    """初始化产品分类"""
    print("📁 初始化产品分类...")
    
    # 检查是否已经初始化过
    result = await session.execute(select(ProductCategory).limit(1))
    if result.scalar_one_or_none() is not None:
        print("  ⚠️  产品分类已存在，跳过初始化")
        # 返回现有分类供后续使用
        result = await session.execute(
            select(ProductCategory).filter(ProductCategory.level == 1)
        )
        return result.scalars().all()
    
    # 一级分类
    cat_food = ProductCategory(
        code="CAT_FOOD",
        name="食品",
        parent_id=None,
        level=1,
        description="各类食品",
        is_active=True,
        sort_order=1
    )
    
    cat_beverage = ProductCategory(
        code="CAT_BEVERAGE",
        name="饮品",
        parent_id=None,
        level=1,
        description="各类饮品",
        is_active=True,
        sort_order=2
    )
    
    session.add_all([cat_food, cat_beverage])
    await session.flush()
    
    # 二级分类
    subcategories = [
        ProductCategory(
            code="CAT_FOOD_MAIN",
            name="主食",
            parent_id=cat_food.id,
            level=2,
            description="米饭、面条等主食",
            is_active=True,
            sort_order=1
        ),
        ProductCategory(
            code="CAT_FOOD_SIDE",
            name="小食",
            parent_id=cat_food.id,
            level=2,
            description="小吃、配菜",
            is_active=True,
            sort_order=2
        ),
        ProductCategory(
            code="CAT_BEV_HOT",
            name="热饮",
            parent_id=cat_beverage.id,
            level=2,
            description="咖啡、奶茶等热饮",
            is_active=True,
            sort_order=1
        ),
        ProductCategory(
            code="CAT_BEV_COLD",
            name="冷饮",
            parent_id=cat_beverage.id,
            level=2,
            description="果汁、冰饮",
            is_active=True,
            sort_order=2
        ),
    ]
    
    session.add_all(subcategories)
    await session.flush()
    
    print(f"  ✅ 创建了 2 个一级分类和 4 个二级分类")
    return subcategories


async def seed_products(session: AsyncSession, categories: list[ProductCategory]):
    """初始化产品数据"""
    print("🍱 初始化产品数据...")
    
    # 检查是否已经初始化过
    result = await session.execute(select(Product).limit(1))
    if result.scalar_one_or_none() is not None:
        print("  ⚠️  产品数据已存在，跳过初始化")
        return
    
    # 获取分类ID
    cat_main = next(c for c in categories if c.code == "CAT_FOOD_MAIN")
    cat_side = next(c for c in categories if c.code == "CAT_FOOD_SIDE")
    cat_hot = next(c for c in categories if c.code == "CAT_BEV_HOT")
    cat_cold = next(c for c in categories if c.code == "CAT_BEV_COLD")
    
    products = [
        # 主食
        Product(
            sku_code="P001",
            name="红烧牛肉盖饭",
            category_id=cat_main.id,
            unit_price=Decimal("38.00"),
            cost_price=Decimal("18.00"),
            unit="份",
            description="经典红烧牛肉盖饭",
            is_active=True,
            is_featured=True,
            sort_order=1
        ),
        Product(
            sku_code="P002",
            name="番茄鸡蛋面",
            category_id=cat_main.id,
            unit_price=Decimal("28.00"),
            cost_price=Decimal("12.00"),
            unit="份",
            description="新鲜番茄配鸡蛋",
            is_active=True,
            is_featured=False,
            sort_order=2
        ),
        
        # 小食
        Product(
            sku_code="P101",
            name="炸鸡翅",
            category_id=cat_side.id,
            unit_price=Decimal("18.00"),
            cost_price=Decimal("8.00"),
            unit="份",
            description="香脆炸鸡翅3只",
            is_active=True,
            is_featured=True,
            sort_order=1
        ),
        Product(
            sku_code="P102",
            name="薯条",
            category_id=cat_side.id,
            unit_price=Decimal("12.00"),
            cost_price=Decimal("5.00"),
            unit="份",
            description="黄金薯条",
            is_active=True,
            is_featured=False,
            sort_order=2
        ),
        
        # 热饮
        Product(
            sku_code="D001",
            name="美式咖啡",
            category_id=cat_hot.id,
            unit_price=Decimal("25.00"),
            cost_price=Decimal("8.00"),
            unit="杯",
            description="经典美式咖啡",
            is_active=True,
            is_featured=True,
            sort_order=1
        ),
        Product(
            sku_code="D002",
            name="奶茶",
            category_id=cat_hot.id,
            unit_price=Decimal("20.00"),
            cost_price=Decimal("7.00"),
            unit="杯",
            description="香浓奶茶",
            is_active=True,
            is_featured=True,
            sort_order=2
        ),
        
        # 冷饮
        Product(
            sku_code="D101",
            name="鲜榨橙汁",
            category_id=cat_cold.id,
            unit_price=Decimal("18.00"),
            cost_price=Decimal("6.00"),
            unit="杯",
            description="新鲜橙子现榨",
            is_active=True,
            is_featured=False,
            sort_order=1
        ),
        Product(
            sku_code="D102",
            name="冰可乐",
            category_id=cat_cold.id,
            unit_price=Decimal("8.00"),
            cost_price=Decimal("3.00"),
            unit="罐",
            description="冰镇可乐",
            is_active=True,
            is_featured=False,
            sort_order=2
        ),
    ]
    
    session.add_all(products)
    print(f"  ✅ 创建了 {len(products)} 个产品")


async def seed_expense_types(session: AsyncSession):
    """初始化费用科目"""
    print("💰 初始化费用科目...")
    
    # 检查是否已经初始化过
    result = await session.execute(select(ExpenseType).limit(1))
    if result.scalar_one_or_none() is not None:
        print("  ⚠️  费用科目已存在，跳过初始化")
        return
    
    # 一级科目
    exp_material = ExpenseType(
        type_code="EXP_MATERIAL",
        name="原材料成本",
        parent_id=None,
        level=1,
        category="cost",
        description="食材、饮料等原材料采购",
        is_active=True,
        sort_order=1
    )
    
    exp_labor = ExpenseType(
        type_code="EXP_LABOR",
        name="人工成本",
        parent_id=None,
        level=1,
        category="cost",
        description="员工工资、福利等",
        is_active=True,
        sort_order=2
    )
    
    exp_rent = ExpenseType(
        type_code="EXP_RENT",
        name="租金",
        parent_id=None,
        level=1,
        category="cost",
        description="门店租金",
        is_active=True,
        sort_order=3
    )
    
    exp_utilities = ExpenseType(
        type_code="EXP_UTILITIES",
        name="水电煤",
        parent_id=None,
        level=1,
        category="cost",
        description="水电煤气费用",
        is_active=True,
        sort_order=4
    )
    
    exp_marketing = ExpenseType(
        type_code="EXP_MARKETING",
        name="营销费用",
        parent_id=None,
        level=1,
        category="expense",
        description="广告、促销等营销费用",
        is_active=True,
        sort_order=5
    )
    
    exp_other = ExpenseType(
        type_code="EXP_OTHER",
        name="其他费用",
        parent_id=None,
        level=1,
        category="expense",
        description="杂项费用",
        is_active=True,
        sort_order=6
    )
    
    session.add_all([exp_material, exp_labor, exp_rent, exp_utilities, exp_marketing, exp_other])
    await session.flush()
    
    # 二级科目
    subcategories = [
        # 原材料细分
        ExpenseType(
            type_code="EXP_MATERIAL_FOOD",
            name="食材采购",
            parent_id=exp_material.id,
            level=2,
            category="cost",
            description="蔬菜、肉类、米面等",
            is_active=True,
            sort_order=1
        ),
        ExpenseType(
            type_code="EXP_MATERIAL_BEV",
            name="饮料采购",
            parent_id=exp_material.id,
            level=2,
            category="cost",
            description="饮料、咖啡豆等",
            is_active=True,
            sort_order=2
        ),
        
        # 人工细分
        ExpenseType(
            type_code="EXP_LABOR_SALARY",
            name="基本工资",
            parent_id=exp_labor.id,
            level=2,
            category="cost",
            description="员工基本工资",
            is_active=True,
            sort_order=1
        ),
        ExpenseType(
            type_code="EXP_LABOR_BONUS",
            name="奖金提成",
            parent_id=exp_labor.id,
            level=2,
            category="cost",
            description="绩效奖金和提成",
            is_active=True,
            sort_order=2
        ),
        
        # 营销细分
        ExpenseType(
            type_code="EXP_MKT_ADS",
            name="广告费",
            parent_id=exp_marketing.id,
            level=2,
            category="expense",
            description="线上线下广告费用",
            is_active=True,
            sort_order=1
        ),
        ExpenseType(
            type_code="EXP_MKT_PROMO",
            name="促销费用",
            parent_id=exp_marketing.id,
            level=2,
            category="expense",
            description="优惠券、满减等促销活动",
            is_active=True,
            sort_order=2
        ),
    ]
    
    session.add_all(subcategories)
    print(f"  ✅ 创建了 6 个一级科目和 6 个二级科目")


async def seed_user_store_permissions(session: AsyncSession):
    """初始化用户门店权限（用于测试数据权限功能）"""
    print("🔑 初始化用户门店权限...")
    
    # 检查是否已经初始化过
    result = await session.execute(select(UserStorePermission).limit(1))
    if result.scalar_one_or_none() is not None:
        print("  ⚠️  用户门店权限已存在，跳过初始化")
        return
    
    # 获取门店和用户（需要重新查询，因为可能是在同一事务内）
    from sqlalchemy import func
    stores_result = await session.execute(select(Store).order_by(Store.id))
    stores = stores_result.scalars().all()
    
    # 获取manager用户
    manager_result = await session.execute(select(User).where(User.username == "manager"))
    manager = manager_result.scalar_one_or_none()
    
    print(f"  调试信息: 找到 {len(stores)} 个门店")
    print(f"  调试信息: manager 用户: {manager is not None}")
    
    if not manager:
        print("  ⚠️  manager 用户不存在，跳过门店权限初始化")
        return
    
    if not stores:
        print("  ⚠️  门店不存在，跳过门店权限初始化")
        return
    
    # 为manager用户分配第一个门店的权限（用于测试数据权限）
    first_store = stores[0]
    permission = UserStorePermission(
        user_id=manager.id,
        store_id=first_store.id
    )
    session.add(permission)
    
    print(f"  ✅ 为 manager 分配了门店权限: {first_store.name} (ID={first_store.id})")
    print(f"  ℹ️  admin 用户为超级管理员，自动拥有所有门店权限")
    print(f"  ℹ️  cashier 用户未分配门店权限，默认可访问所有门店（向后兼容）")


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🌱 开始初始化种子数据...")
    print("="*60 + "\n")
    
    async with AsyncSessionLocal() as session:
        try:
            # 执行种子数据初始化
            await seed_users_and_permissions(session)
            await seed_stores(session)
            categories = await seed_product_categories(session)
            await seed_products(session, categories)
            await seed_expense_types(session)
            await seed_user_store_permissions(session)
            
            # 提交事务
            await session.commit()
            
            print("\n" + "="*60)
            print("✅ 种子数据初始化完成！")
            print("="*60)
            print("\n📝 测试账号：")
            print("  - 管理员: admin / Admin@123")
            print("  - 门店经理: manager / Manager@123")
            print("  - 收银员: cashier / Cashier@123")
            print()
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 初始化失败: {str(e)}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
