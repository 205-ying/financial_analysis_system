"""
批量生成验证数据脚本

生成符合实际业务逻辑的大量测试数据
包括：用户、门店、产品、订单、费用、KPI数据等

使用方法：
python backend/scripts/generate_bulk_data.py
"""
import asyncio
import sys
from pathlib import Path
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

# 添加项目根目录到 Python 路径
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, Role, user_role
from app.models.store import Store, ProductCategory, Product
from app.models.order import OrderHeader, OrderItem
from app.models.expense import ExpenseType, ExpenseRecord
from app.models.kpi import KpiDailyStore


# 中国常见姓氏和名字
LAST_NAMES = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周"]
FIRST_NAMES = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军"]
BJ_DISTRICTS = ["朝阳区", "海淀区", "东城区", "西城区", "丰台区"]
BJ_LANDMARKS = ["中关村", "三里屯", "望京", "国贸", "西单", "王府井", "五道口"]

def random_name() -> str:
    """生成随机中文姓名"""
    return random.choice(LAST_NAMES) + random.choice(FIRST_NAMES)

def random_phone() -> str:
    """生成随机手机号"""
    return "138" + "".join([str(random.randint(0, 9)) for _ in range(8)])

def random_address() -> str:
    """生成随机北京地址"""
    return f"北京市{random.choice(BJ_DISTRICTS)}{random.choice(BJ_LANDMARKS)}{random.randint(1, 200)}号"


async def generate_users(session: AsyncSession, count: int) -> list[User]:
    """生成用户"""
    print(f"👤 生成 {count} 个用户...")
    
    result = await session.execute(select(Role))
    roles = result.scalars().all()
    role_map = {r.code: r for r in roles}
    
    result = await session.execute(select(func.count(User.id)))
    start_num = result.scalar()
    
    users = []
    for i in range(count):
        role_code = random.choices(["cashier", "manager", "accountant"], weights=[60, 30, 10], k=1)[0]
        username = f"{role_code}{start_num + i + 1:03d}"
        
        user = User(
            username=username,
            email=f"{username}@example.com",
            password_hash=hash_password("Test@123"),
            full_name=random_name(),
            phone=random_phone(),
            is_active=True,
            is_superuser=False
        )
        users.append(user)
        session.add(user)
    
    await session.flush()
    
    # 分配角色
    for user in users:
        for code in ["cashier", "manager", "accountant"]:
            if code in user.username:
                await session.execute(user_role.insert().values(user_id=user.id, role_id=role_map[code].id))
                break
    
    print(f"  ✅ 创建了 {len(users)} 个用户")
    return users


async def generate_stores(session: AsyncSession, count: int) -> list[Store]:
    """生成门店"""
    print(f"🏪 生成 {count} 个门店...")
    
    result = await session.execute(select(func.count(Store.id)))
    start_num = result.scalar()
    
    stores = []
    for i in range(count):
        code = f"S{start_num + i + 1:03d}"
        landmark = random.choice(BJ_LANDMARKS)
        
        store = Store(
            code=code,
            name=f"{landmark}店",
            address=random_address(),
            phone=random_phone(),
            contact_person=random_name(),
            business_hours="10:00-22:00",
            area_sqm=Decimal(str(random.randint(100, 250))),
            is_active=True,
            sort_order=start_num + i + 1
        )
        stores.append(store)
        session.add(store)
    
    await session.flush()
    print(f"  ✅ 创建了 {len(stores)} 个门店")
    return stores


async def generate_products(session: AsyncSession, count: int) -> list[Product]:
    """生成产品"""
    print(f"🍱 生成 {count} 个产品...")
    
    result = await session.execute(select(ProductCategory).filter(ProductCategory.level == 2))
    categories = result.scalars().all()
    
    result = await session.execute(select(func.count(Product.id)))
    start_num = result.scalar()
    
    products = []
    for i in range(count):
        category = random.choice(categories)
        sku = f"P{start_num + i + 1:04d}"
        unit_price = Decimal(str(random.randint(10, 60)))
        cost_price = (unit_price * Decimal(str(random.uniform(0.3, 0.6)))).quantize(Decimal("0.01"))
        
        product = Product(
            sku_code=sku,
            name=f"产品{start_num + i + 1}",
            category_id=category.id,
            unit_price=unit_price,
            cost_price=cost_price,
            unit="份",
            description="测试产品",
            is_active=True,
            is_featured=random.random() > 0.7,
            sort_order=start_num + i + 1
        )
        products.append(product)
        session.add(product)
    
    await session.flush()
    print(f"  ✅ 创建了 {len(products)} 个产品")
    return products


async def generate_orders_for_period(
    session: AsyncSession,
    stores: list[Store],
    products: list[Product],
    start_date: date,
    days: int,
    start_counter: int
) -> int:
    """生成指定时间段的订单"""
    active_products = [p for p in products if p.is_active]
    counter = start_counter
    total_orders = 0
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        is_weekend = current_date.weekday() >= 5
        daily_orders = random.randint(80, 120) if not is_weekend else random.randint(120, 180)
        
        # 批量创建订单
        orders_batch = []
        for _ in range(daily_orders):
            store = random.choice(stores)
            order_no = f"ORD{counter:010d}"
            counter += 1
            
            hour = random.randint(10, 21)
            minute = random.randint(0, 59)
            order_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
            
            # 计算订单金额
            item_count = random.choices([1, 2, 3], weights=[50, 35, 15], k=1)[0]
            gross_amount = Decimal("0")
            for _ in range(item_count):
                product = random.choice(active_products)
                quantity = random.randint(1, 2)
                gross_amount += product.unit_price * quantity
            
            discount = Decimal("0")
            if random.random() < 0.1:
                discount = (gross_amount * Decimal(str(random.uniform(0.05, 0.15)))).quantize(Decimal("0.01"))
            
            net_amount = gross_amount - discount
            
            order = OrderHeader(
                order_no=order_no,
                store_id=store.id,
                biz_date=current_date,
                order_time=order_time,
                channel=random.choice(["dine_in", "takeout", "delivery"]),
                table_no=f"T{random.randint(1, 30):02d}" if random.random() > 0.5 else None,
                gross_amount=gross_amount,
                discount_amount=discount,
                net_amount=net_amount,
                payment_method=random.choice(["alipay", "wechat", "cash"]),
                status="completed",
                customer_name=random_name() if random.random() > 0.3 else None,
                customer_phone=random_phone() if random.random() > 0.7 else None
            )
            orders_batch.append(order)
            session.add(order)
        
        # 每天提交一次
        await session.flush()
        
        # 为订单添加明细
        for order in orders_batch:
            item_count = random.choices([1, 2, 3], weights=[50, 35, 15], k=1)[0]
            for _ in range(item_count):
                product = random.choice(active_products)
                quantity = Decimal(str(random.randint(1, 2)))
                line_amount = (product.unit_price * quantity).quantize(Decimal("0.01"))
                
                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_sku=product.sku_code,
                    product_name=product.name,
                    unit=product.unit,
                    quantity=quantity,
                    unit_price=product.unit_price,
                    line_amount=line_amount,
                    discount_amount=Decimal("0")
                )
                session.add(item)
        
        await session.flush()
        total_orders += daily_orders
        
        if (day_offset + 1) % 30 == 0:
            print(f"  📊 已生成 {day_offset + 1}/{days} 天的订单...")
    
    return counter


async def generate_expenses_for_period(
    session: AsyncSession,
    stores: list[Store],
    expense_types: list[ExpenseType],
    users: list[User],
    start_date: date,
    days: int
):
    """生成指定时间段的费用"""
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        
        for store in stores:
            # 每日费用：食材、饮料
            if random.random() < 0.8:
                for type_code in ["EXP_MATERIAL_FOOD", "EXP_MATERIAL_BEV"]:
                    exp_type = next((et for et in expense_types if et.type_code == type_code), None)
                    if exp_type:
                        amount = Decimal(str(random.randint(500, 2000)))
                        expense = ExpenseRecord(
                            expense_type_id=exp_type.id,
                            store_id=store.id,
                            biz_date=current_date,
                            amount=amount,
                            payment_method=random.choice(["alipay", "wechat", "cash"]),
                            status="approved",
                            created_by=random.choice(users).id,
                            approved_by=random.choice(users).id if random.random() > 0.2 else None
                        )
                        session.add(expense)
            
            # 每月费用
            if current_date.day == 1:
                for type_code in ["EXP_LABOR_SALARY", "EXP_RENT"]:
                    exp_type = next((et for et in expense_types if et.type_code == type_code), None)
                    if exp_type:
                        amount = Decimal(str(random.randint(15000, 25000)))
                        expense = ExpenseRecord(
                            expense_type_id=exp_type.id,
                            store_id=store.id,
                            biz_date=current_date,
                            amount=amount,
                            payment_method="bank",
                            status="approved",
                            created_by=random.choice(users).id,
                            approved_by=random.choice(users).id
                        )
                        session.add(expense)
        
        if (day_offset + 1) % 30 == 0:
            await session.flush()


async def generate_kpi_for_period(
    session: AsyncSession,
    stores: list[Store],
    start_date: date,
    days: int
):
    """生成KPI数据"""
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        
        for store in stores:
            # 查询订单数据
            result = await session.execute(
                select(
                    func.count(OrderHeader.id),
                    func.coalesce(func.sum(OrderHeader.gross_amount), 0),
                    func.coalesce(func.sum(OrderHeader.discount_amount), 0),
                    func.coalesce(func.sum(OrderHeader.net_amount), 0)
                ).filter(
                    OrderHeader.store_id == store.id,
                    OrderHeader.biz_date == current_date,
                    OrderHeader.status == "completed"
                )
            )
            order_count, revenue, discount, net_revenue = result.one()
            
            # 查询费用
            result = await session.execute(
                select(func.coalesce(func.sum(ExpenseRecord.amount), 0))
                .filter(
                    ExpenseRecord.store_id == store.id,
                    ExpenseRecord.biz_date == current_date,
                    ExpenseRecord.status == "approved"
                )
            )
            cost = result.scalar() or Decimal("0")
            
            if order_count > 0:
                revenue = Decimal(str(revenue))
                net_revenue = Decimal(str(net_revenue))
                discount = Decimal(str(discount))
                cost_total = cost
                gross_profit = net_revenue - cost_total
                profit_rate = (gross_profit / net_revenue) if net_revenue > 0 else Decimal("0")
                # 限制profit_rate范围在 -9.9999 到 9.9999
                if profit_rate > Decimal("9.9999"):
                    profit_rate = Decimal("9.9999")
                elif profit_rate < Decimal("-9.9999"):
                    profit_rate = Decimal("-9.9999")
                
                kpi = KpiDailyStore(
                    biz_date=current_date,
                    store_id=store.id,
                    revenue=revenue,
                    discount_amount=discount,
                    net_revenue=net_revenue,
                    cost_total=cost_total,
                    gross_profit=gross_profit,
                    operating_profit=gross_profit,
                    profit_rate=profit_rate.quantize(Decimal("0.0001")),
                    order_count=order_count,
                    customer_count=order_count,
                    avg_order_value=(net_revenue / order_count).quantize(Decimal("0.01"))
                )
                session.add(kpi)
        
        if (day_offset + 1) % 30 == 0:
            await session.flush()


async def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 开始生成大量验证数据...")
    print("="*70 + "\n")
    
    config = {
        "users": 20,
        "stores": 10,
        "products": 60,
        "days": 180
    }
    
    print("📋 配置：")
    for key, value in config.items():
        print(f"  - {key}: {value}")
    print()
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. 生成用户
            users = await generate_users(session, config["users"])
            await session.commit()
            
            # 2. 生成门店
            stores = await generate_stores(session, config["stores"])
            await session.commit()
            
            # 3. 生成产品
            products = await generate_products(session, config["products"])
            await session.commit()
            
            # 4. 获取费用科目
            result = await session.execute(select(ExpenseType).filter(ExpenseType.level == 2))
            expense_types = result.scalars().all()
            
            # 5. 获取起始订单号
            result = await session.execute(
                select(func.max(OrderHeader.order_no)).filter(OrderHeader.order_no.like('ORD%'))
            )
            max_order_no = result.scalar()
            if max_order_no and max_order_no.startswith('ORD'):
                counter = int(max_order_no[3:]) + 1
            else:
                counter = 1
            
            # 6. 生成订单
            print(f"📋 生成最近 {config['days']} 天的订单...")
            start_date = date.today() - timedelta(days=config["days"])
            final_counter = await generate_orders_for_period(
                session, stores, products, start_date, config["days"], counter
            )
            print(f"  ✅ 共创建了约 {(final_counter - counter)} 个订单")
            await session.commit()
            
            # 7. 生成费用
            print(f"💰 生成最近 {config['days']} 天的费用...")
            await generate_expenses_for_period(session, stores, expense_types, users, start_date, config["days"])
            print(f"  ✅ 费用记录已生成")
            await session.commit()
            
            # 8. 生成KPI
            print(f"📊 生成最近 {config['days']} 天的KPI...")
            await generate_kpi_for_period(session, stores, start_date, config["days"])
            print(f"  ✅ KPI记录已生成")
            await session.commit()
            
            print("\n" + "="*70)
            print("✅ 数据生成完成！")
            print("="*70)
            print("\n💡 提示：所有新用户的默认密码为: Test@123\n")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
