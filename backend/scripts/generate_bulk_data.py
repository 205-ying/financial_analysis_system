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
LAST_NAMES = ["王", "李", "张", "刘", "陈", "杨", "黄", "赵", "吴", "周", "徐", "孙", "马", "朱", "胡", "郭", "何", "林", "罗", "高"]
FIRST_NAMES = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "秀兰", "霞", "明", "超", "刚", "平"]
MIDDLE_NAMES = ["", "小", "大", "老", "阿"]
BJ_DISTRICTS = ["朝阳区", "海淀区", "东城区", "西城区", "丰台区", "石景山区", "通州区", "昌平区"]
BJ_LANDMARKS = ["中关村", "三里屯", "望京", "国贸", "西单", "王府井", "五道口", "亚运村", "公主坟", "西二旗"]

# 详细的中餐菜品数据
DISH_DATA = {
    "川菜": [
        ("宫保鸡丁", 38, 15), ("麻婆豆腐", 28, 10), ("水煮鱼", 68, 30), 
        ("回锅肉", 42, 18), ("鱼香肉丝", 35, 14), ("辣子鸡", 45, 20),
        ("毛血旺", 58, 25), ("夫妻肺片", 36, 16), ("口水鸡", 38, 17),
        ("蒜泥白肉", 32, 14), ("酸菜鱼", 65, 28), ("麻辣香锅", 55, 24)
    ],
    "粤菜": [
        ("白切鸡", 48, 22), ("烧鹅", 88, 40), ("蜜汁叉烧", 52, 24),
        ("糖醋排骨", 45, 20), ("广式烧鸭", 78, 35), ("盐焗鸡", 65, 30),
        ("清蒸鲈鱼", 68, 32), ("蒸排骨", 42, 19), ("菠萝咕咾肉", 38, 16)
    ],
    "家常菜": [
        ("番茄炒蛋", 22, 8), ("青椒肉丝", 28, 12), ("鱼香茄子", 26, 10),
        ("醋溜白菜", 18, 6), ("红烧肉", 45, 20), ("糖醋里脊", 38, 16),
        ("酱爆鸡丁", 35, 15), ("蒜蓉西兰花", 20, 7), ("干煸豆角", 24, 9),
        ("木须肉", 32, 14), ("地三鲜", 28, 11), ("虎皮青椒", 22, 8)
    ],
    "凉菜": [
        ("拍黄瓜", 15, 5), ("凉拌三丝", 18, 6), ("皮蛋豆腐", 22, 8),
        ("凉拌木耳", 20, 7), ("蒜泥菠菜", 16, 5), ("酸辣土豆丝", 18, 6),
        ("麻辣豆干", 20, 7), ("花生米", 15, 4), ("海带丝", 18, 6)
    ],
    "面点": [
        ("牛肉面", 28, 12), ("炸酱面", 25, 10), ("担担面", 26, 11),
        ("刀削面", 24, 10), ("阳春面", 18, 7), ("馄饨", 22, 9),
        ("小笼包", 25, 10), ("煎饺", 22, 9), ("蒸饺", 20, 8),
        ("炒饭", 20, 8), ("盖浇饭", 25, 10), ("石锅拌饭", 32, 14)
    ],
    "汤品": [
        ("酸辣汤", 18, 6), ("紫菜蛋汤", 15, 5), ("西红柿蛋汤", 16, 5),
        ("玉米排骨汤", 35, 15), ("老鸭汤", 45, 20), ("冬瓜排骨汤", 28, 12)
    ],
    "饮品": [
        ("珍珠奶茶", 15, 4), ("柠檬茶", 12, 3), ("红茶", 8, 2),
        ("绿茶", 8, 2), ("可乐", 10, 3), ("雪碧", 10, 3),
        ("鲜榨橙汁", 18, 6), ("西瓜汁", 15, 5), ("酸梅汤", 12, 4),
        ("豆浆", 8, 2), ("牛奶", 10, 3), ("咖啡", 20, 6)
    ]
}

def random_name() -> str:
    """生成随机中文姓名"""
    middle = random.choice(MIDDLE_NAMES)
    first = random.choice(FIRST_NAMES)
    return random.choice(LAST_NAMES) + middle + first

def random_phone() -> str:
    """生成随机手机号"""
    return "138" + "".join([str(random.randint(0, 9)) for _ in range(8)])

def random_address() -> str:
    """生成随机北京地址"""
    district = random.choice(BJ_DISTRICTS)
    landmark = random.choice(BJ_LANDMARKS)
    building = random.choice(["大厦", "广场", "商业中心", "购物中心", "SOHO", "写字楼", "商务区"])
    return f"北京市{district}{landmark}{building}{random.randint(1, 20)}号楼{random.randint(1, 8)}层"


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
    
    store_types = ["旗舰店", "标准店", "社区店", "商圈店"]
    business_hours_options = ["09:00-22:00", "10:00-22:00", "10:00-23:00", "11:00-21:00"]
    
    stores = []
    for i in range(count):
        code = f"BJ{start_num + i + 1:03d}"
        landmark = random.choice(BJ_LANDMARKS)
        store_type = random.choice(store_types)
        
        store = Store(
            code=code,
            name=f"味道中国{landmark}{store_type}",
            address=random_address(),
            phone=random_phone(),
            contact_person=random_name(),
            business_hours=random.choice(business_hours_options),
            area_sqm=Decimal(str(random.randint(150, 350))),
            is_active=True,
            sort_order=start_num + i + 1
        )
        stores.append(store)
        session.add(store)
    
    await session.flush()
    print(f"  ✅ 创建了 {len(stores)} 个门店")
    return stores


async def generate_products(session: AsyncSession, count: int = None) -> list[Product]:
    """生成产品（使用真实菜品名称）"""
    
    result = await session.execute(select(ProductCategory).filter(ProductCategory.level == 2))
    categories = result.scalars().all()
    category_map = {cat.name: cat for cat in categories}
    
    result = await session.execute(select(func.count(Product.id)))
    start_num = result.scalar()
    
    products = []
    sku_counter = start_num + 1
    
    # 为每个菜品类别生成产品
    for dish_category, dishes in DISH_DATA.items():
        # 找到对应的数据库分类（尽量匹配）
        db_category = None
        if dish_category in ["川菜", "粤菜", "家常菜"]:
            db_category = category_map.get("热菜")
        elif dish_category == "凉菜":
            db_category = category_map.get("凉菜")
        elif dish_category == "面点":
            db_category = category_map.get("主食")
        elif dish_category == "汤品":
            db_category = category_map.get("汤类")
        elif dish_category == "饮品":
            db_category = category_map.get("饮品")
        
        if not db_category:
            db_category = random.choice(categories)
        
        for dish_name, price, cost in dishes:
            product = Product(
                sku_code=f"P{sku_counter:04d}",
                name=dish_name,
                category_id=db_category.id,
                unit_price=Decimal(str(price)),
                cost_price=Decimal(str(cost)),
                unit="份",
                description=f"{dish_category} - {dish_name}",
                is_active=True,
                is_featured=random.random() > 0.75,  # 25%的菜品为招牌菜
                sort_order=sku_counter
            )
            products.append(product)
            session.add(product)
            sku_counter += 1
    
    await session.flush()
    print(f"  ✅ 创建了 {len(products)} 个产品（包含{len(DISH_DATA)}个类别的真实菜品）")
    return products


async def generate_orders_for_period(
    session: AsyncSession,
    stores: list[Store],
    products: list[Product],
    start_date: date,
    days: int,
    start_counter: int
) -> int:
    """生成指定时间段的订单（更真实的时间分布）"""
    active_products = [p for p in products if p.is_active]
    counter = start_counter
    total_orders = 0
    
    # 按菜品类别分组，方便生成合理的组合
    hot_dishes = [p for p in active_products if "麻婆豆腐" in p.name or "宫保鸡丁" in p.name or "回锅肉" in p.name or "鱼香肉丝" in p.name or p.unit_price >= 30]
    cold_dishes = [p for p in active_products if "拍黄瓜" in p.name or "凉拌" in p.name or p.unit_price <= 25]
    staple_foods = [p for p in active_products if "面" in p.name or "饭" in p.name or "饺" in p.name or "包" in p.name]
    beverages = [p for p in active_products if "茶" in p.name or "可乐" in p.name or "汁" in p.name or "奶" in p.name or "咖啡" in p.name]
    soups = [p for p in active_products if "汤" in p.name]
    
    # 如果某些类别为空，用全部产品兜底
    if not hot_dishes: hot_dishes = active_products
    if not cold_dishes: cold_dishes = active_products
    if not staple_foods: staple_foods = active_products
    if not beverages: beverages = active_products
    if not soups: soups = active_products
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        is_weekend = current_date.weekday() >= 5
        
        # 周末订单更多
        base_orders = 120 if not is_weekend else 180
        daily_orders = random.randint(int(base_orders * 0.9), int(base_orders * 1.1))
        
        # 时间分布：11:00-14:00午餐高峰，17:00-21:00晚餐高峰
        order_times = []
        for _ in range(daily_orders):
            # 60%午餐高峰，30%晚餐高峰，10%其他时间
            time_slot = random.choices(["lunch", "dinner", "other"], weights=[60, 30, 10], k=1)[0]
            if time_slot == "lunch":
                hour = random.randint(11, 13)
                minute = random.randint(0, 59)
            elif time_slot == "dinner":
                hour = random.randint(17, 20)
                minute = random.randint(0, 59)
            else:
                hour = random.randint(10, 21)
                minute = random.randint(0, 59)
            order_times.append((hour, minute))
        
        order_times.sort()  # 按时间排序
        
        # 批量创建订单
        orders_batch = []
        for hour, minute in order_times:
            store = random.choice(stores)
            order_no = f"ORD{counter:010d}"
            counter += 1
            
            order_time = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)
            
            # 计算订单金额（预先计算以设置订单头）
            item_count = random.choices([1, 2, 3, 4], weights=[20, 40, 30, 10], k=1)[0]
            gross_amount = Decimal("0")
            
            # 根据就餐类型选择不同的菜品组合
            meal_type = random.choices(["set_meal", "simple", "luxury"], weights=[50, 30, 20], k=1)[0]
            
            # 临时存储订单项用于后续创建
            temp_items = []
            
            if meal_type == "set_meal":  # 套餐：热菜+主食+饮料
                # 1-2个热菜
                for _ in range(random.randint(1, 2)):
                    product = random.choice(hot_dishes)
                    quantity = 1
                    temp_items.append((product, quantity))
                # 1个主食
                product = random.choice(staple_foods)
                temp_items.append((product, 1))
                # 可能有饮料
                if random.random() > 0.3:
                    product = random.choice(beverages)
                    temp_items.append((product, random.randint(1, 2)))
            elif meal_type == "simple":  # 简单餐：主食或快餐
                product = random.choice(staple_foods)
                temp_items.append((product, 1))
                if random.random() > 0.5:
                    product = random.choice(beverages)
                    temp_items.append((product, 1))
            else:  # 豪华餐：多个热菜+凉菜+汤+主食+饮料
                # 2-3个热菜
                for _ in range(random.randint(2, 3)):
                    product = random.choice(hot_dishes)
                    temp_items.append((product, 1))
                # 1个凉菜
                product = random.choice(cold_dishes)
                temp_items.append((product, 1))
                # 可能有汤
                if random.random() > 0.5:
                    product = random.choice(soups)
                    temp_items.append((product, 1))
                # 主食
                product = random.choice(staple_foods)
                temp_items.append((product, random.randint(1, 2)))
                # 饮料
                if random.random() > 0.3:
                    product = random.choice(beverages)
                    temp_items.append((product, random.randint(1, 3)))
            
            # 计算总金额
            for product, quantity in temp_items:
                gross_amount += product.unit_price * quantity
            
            # 折扣：10%的订单有折扣
            discount = Decimal("0")
            if random.random() < 0.1:
                discount = (gross_amount * Decimal(str(random.uniform(0.05, 0.2)))).quantize(Decimal("0.01"))
            
            net_amount = gross_amount - discount
            
            # 渠道分布：堂食60%，外卖30%，自提10%
            channel = random.choices(["dine_in", "delivery", "takeout"], weights=[60, 30, 10], k=1)[0]
            
            order = OrderHeader(
                order_no=order_no,
                store_id=store.id,
                biz_date=current_date,
                order_time=order_time,
                channel=channel,
                table_no=f"T{random.randint(1, 30):02d}" if channel == "dine_in" else None,
                gross_amount=gross_amount,
                discount_amount=discount,
                net_amount=net_amount,
                payment_method=random.choices(["alipay", "wechat", "cash", "card"], weights=[40, 40, 15, 5], k=1)[0],
                status="completed",
                customer_name=random_name() if random.random() > 0.4 else None,
                customer_phone=random_phone() if random.random() > 0.5 else None,
                remark=random.choice(["", "", "", "少油少盐", "不要辣", "多加辣", "打包"]) if random.random() > 0.8 else None
            )
            orders_batch.append((order, temp_items))
            session.add(order)
        
        # 每天提交一次订单头
        await session.flush()
        
        # 为订单添加明细
        for order, temp_items in orders_batch:
            for product, quantity in temp_items:
                quantity_decimal = Decimal(str(quantity))
                line_amount = (product.unit_price * quantity_decimal).quantize(Decimal("0.01"))
                
                item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_sku=product.sku_code,
                    product_name=product.name,
                    unit=product.unit,
                    quantity=quantity_decimal,
                    unit_price=product.unit_price,
                    line_amount=line_amount,
                    discount_amount=Decimal("0")
                )
                session.add(item)
        
        await session.flush()
        total_orders += daily_orders
        
        if (day_offset + 1) % 30 == 0 or day_offset == days - 1:
            print(f"  📊 已生成 {day_offset + 1}/{days} 天的订单（共约 {total_orders} 单）...")
    
    return counter


async def generate_expenses_for_period(
    session: AsyncSession,
    stores: list[Store],
    expense_types: list[ExpenseType],
    users: list[User],
    start_date: date,
    days: int
):
    """生成指定时间段的费用（更详细的中文描述）"""
    
    # 食材供应商
    food_suppliers = ["新发地蔬菜批发市场", "顺义农副产品批发市场", "永辉超市", "麦德龙", "物美"]
    beverage_suppliers = ["康师傅经销商", "统一饮品", "可口可乐公司", "百事北京分公司", "农夫山泉"]
    
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)
        
        for store in stores:
            # 每日费用：食材、饮料（80%概率发生）
            if random.random() < 0.8:
                # 食材采购
                exp_type = next((et for et in expense_types if et.type_code == "EXP_MATERIAL_FOOD"), None)
                if exp_type:
                    amount = Decimal(str(random.randint(800, 2500)))
                    supplier = random.choice(food_suppliers)
                    expense = ExpenseRecord(
                        expense_type_id=exp_type.id,
                        store_id=store.id,
                        biz_date=current_date,
                        amount=amount,
                        payment_method=random.choice(["alipay", "wechat", "bank"]),
                        status="approved",
                        description=f"{supplier} - 采购食材（蔬菜、肉类、调料等）",
                        vendor=supplier,
                        invoice_no=f"INV{current_date.strftime('%Y%m%d')}{store.id:03d}{random.randint(1000, 9999)}",
                        created_by=random.choice(users).id,
                        approved_by=random.choice(users).id
                    )
                    session.add(expense)
                
                # 饮料采购（60%概率）
                if random.random() < 0.6:
                    exp_type = next((et for et in expense_types if et.type_code == "EXP_MATERIAL_BEV"), None)
                    if exp_type:
                        amount = Decimal(str(random.randint(300, 1000)))
                        supplier = random.choice(beverage_suppliers)
                        expense = ExpenseRecord(
                            expense_type_id=exp_type.id,
                            store_id=store.id,
                            biz_date=current_date,
                            amount=amount,
                            payment_method=random.choice(["alipay", "wechat", "bank"]),
                            status="approved",
                            description=f"{supplier} - 采购饮料（茶饮、软饮、果汁等）",
                            vendor=supplier,
                            invoice_no=f"INV{current_date.strftime('%Y%m%d')}{store.id:03d}{random.randint(1000, 9999)}",
                            created_by=random.choice(users).id,
                            approved_by=random.choice(users).id
                        )
                        session.add(expense)
            
            # 每周费用（周一）
            if current_date.weekday() == 0:
                # 清洁用品
                exp_type = next((et for et in expense_types if "清洁" in et.name or "消毒" in et.name), None)
                if exp_type:
                    amount = Decimal(str(random.randint(200, 500)))
                    expense = ExpenseRecord(
                        expense_type_id=exp_type.id,
                        store_id=store.id,
                        biz_date=current_date,
                        amount=amount,
                        payment_method="alipay",
                        status="approved",
                        description="采购清洁用品（洗洁精、消毒液、抹布等）",
                        vendor="京东自营",
                        created_by=random.choice(users).id,
                        approved_by=random.choice(users).id
                    )
                    session.add(expense)
            
            # 每月费用（每月1号）
            if current_date.day == 1:
                # 工资
                exp_type = next((et for et in expense_types if et.type_code == "EXP_LABOR_SALARY"), None)
                if exp_type:
                    # 根据门店面积估算员工数量和工资
                    staff_count = int(store.area_sqm / 30)  # 每30平米1个员工
                    avg_salary = random.randint(5000, 8000)
                    amount = Decimal(str(staff_count * avg_salary))
                    expense = ExpenseRecord(
                        expense_type_id=exp_type.id,
                        store_id=store.id,
                        biz_date=current_date,
                        amount=amount,
                        payment_method="bank",
                        status="approved",
                        description=f"{current_date.strftime('%Y年%m月')}工资 - {staff_count}名员工",
                        created_by=random.choice(users).id,
                        approved_by=random.choice(users).id
                    )
                    session.add(expense)
                
                # 房租
                exp_type = next((et for et in expense_types if et.type_code == "EXP_RENT"), None)
                if exp_type:
                    # 按面积和地段计算租金（每平米100-300元/月）
                    rent_per_sqm = random.randint(150, 280)
                    amount = Decimal(str(int(store.area_sqm * rent_per_sqm)))
                    expense = ExpenseRecord(
                        expense_type_id=exp_type.id,
                        store_id=store.id,
                        biz_date=current_date,
                        amount=amount,
                        payment_method="bank",
                        status="approved",
                        description=f"{current_date.strftime('%Y年%m月')}房租 - {store.area_sqm}平米 × {rent_per_sqm}元/月",
                        vendor=f"{store.address.split('北京市')[1].split('区')[0]}区物业管理公司",
                        created_by=random.choice(users).id,
                        approved_by=random.choice(users).id
                    )
                    session.add(expense)
                
                # 水电费
                exp_type = next((et for et in expense_types if "水电" in et.name or "能源" in et.name), None)
                if exp_type:
                    amount = Decimal(str(random.randint(2000, 5000)))
                    expense = ExpenseRecord(
                        expense_type_id=exp_type.id,
                        store_id=store.id,
                        biz_date=current_date,
                        amount=amount,
                        payment_method="bank",
                        status="approved",
                        description=f"{current_date.strftime('%Y年%m月')}水电费用",
                        vendor="北京市电力公司",
                        created_by=random.choice(users).id,
                        approved_by=random.choice(users).id
                    )
                    session.add(expense)
        
        if (day_offset + 1) % 30 == 0 or day_offset == days - 1:
            await session.flush()
            print(f"  💰 已生成 {day_offset + 1}/{days} 天的费用记录...")



async def generate_kpi_for_period(
    session: AsyncSession,
    stores: list[Store],
    start_date: date,
    days: int
):
    """生成KPI数据"""
    total_kpi = 0
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
                total_kpi += 1
        
        if (day_offset + 1) % 30 == 0 or day_offset == days - 1:
            await session.flush()
            print(f"  📊 已生成 {day_offset + 1}/{days} 天的KPI记录（共 {total_kpi} 条）...")



async def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 开始生成大量详细的测试数据...")
    print("="*70 + "\n")
    
    config = {
        "users": 30,      # 增加到30个用户
        "stores": 15,     # 增加到15个门店
        "days": 365       # 生成一整年的数据
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
            
            # 3. 生成产品（使用真实菜品，生成所有预定义的菜品）
            print(f"🍱 生成产品（真实菜品）...")
            products = await generate_products(session)
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
            print(f"📋 生成最近 {config['days']} 天的订单（包含真实时间分布）...")
            start_date = date.today() - timedelta(days=config["days"])
            final_counter = await generate_orders_for_period(
                session, stores, products, start_date, config["days"], counter
            )
            total_orders = final_counter - counter
            print(f"  ✅ 共创建了 {total_orders:,} 个订单")
            await session.commit()
            
            # 7. 生成费用
            print(f"💰 生成最近 {config['days']} 天的费用（包含详细描述）...")
            await generate_expenses_for_period(session, stores, expense_types, users, start_date, config["days"])
            
            # 统计费用记录数
            result = await session.execute(select(func.count(ExpenseRecord.id)))
            expense_count = result.scalar()
            print(f"  ✅ 共创建了 {expense_count:,} 条费用记录")
            await session.commit()
            
            # 8. 生成KPI
            print(f"📊 生成最近 {config['days']} 天的KPI...")
            await generate_kpi_for_period(session, stores, start_date, config["days"])
            
            # 统计KPI记录数
            result = await session.execute(select(func.count(KpiDailyStore.id)))
            kpi_count = result.scalar()
            print(f"  ✅ 共创建了 {kpi_count:,} 条KPI记录")
            await session.commit()
            
            print("\n" + "="*70)
            print("✅ 数据生成完成！")
            print("="*70)
            print("\n📊 数据统计：")
            print(f"  - 用户数：{config['users']} 个")
            print(f"  - 门店数：{config['stores']} 个")
            print(f"  - 产品数：{len(products)} 个（真实菜品）")
            print(f"  - 订单数：{total_orders:,} 个")
            print(f"  - 费用记录：{expense_count:,} 条")
            print(f"  - KPI记录：{kpi_count:,} 条")
            print(f"  - 时间范围：{start_date.strftime('%Y-%m-%d')} 至 {date.today().strftime('%Y-%m-%d')}")
            print("\n💡 提示：")
            print("  - 所有新用户的默认密码为: Test@123")
            print("  - 订单时间分布包含午餐和晚餐高峰期")
            print("  - 费用记录包含详细的供应商和描述信息")
            print("  - 菜品包含川菜、粤菜、家常菜、凉菜、面点、汤品、饮品等多个类别\n")
            
        except Exception as e:
            await session.rollback()
            print(f"\n❌ 生成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise


if __name__ == "__main__":
    asyncio.run(main())
