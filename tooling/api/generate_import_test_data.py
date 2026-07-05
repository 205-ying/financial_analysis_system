"""
生成数据导入功能测试文件

生成符合导入格式要求的测试数据文件（Excel和CSV格式）
包括：订单数据、费用记录、门店信息、费用科目

使用方法：
python tooling/api/generate_import_test_data.py
"""
import sys
from pathlib import Path
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
import pandas as pd

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve()
while project_root != project_root.parent and not (project_root / "services" / "api" / "app").exists():
    project_root = project_root.parent
backend_dir = project_root / "services" / "api"
sys.path.insert(0, str(backend_dir))

# 输出目录
OUTPUT_DIR = Path("services/api/test_data")

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


def generate_orders_data(count: int = 50, start_date: date = None) -> pd.DataFrame:
    """
    生成订单导入测试数据
    
    必需字段：
    - order_no: 订单号（唯一）
    - biz_date: 业务日期 (YYYY-MM-DD)
    - gross_amount: 总金额
    - discount_amount: 折扣金额
    - net_amount: 实收金额
    
    可选字段：
    - channel: 渠道 (dine_in|takeout|delivery)
    - payment_method: 支付方式 (cash|alipay|wechat|bank)
    - customer_name: 客户姓名
    - customer_phone: 客户电话
    - table_no: 桌号
    """
    print(f"📋 生成 {count} 条订单数据...")
    
    if start_date is None:
        start_date = date.today() - timedelta(days=30)
    
    orders = []
    order_counter = 10000  # 起始订单号
    
    for i in range(count):
        # 随机日期（最近30天）
        days_offset = random.randint(0, 29)
        biz_date = start_date + timedelta(days=days_offset)
        
        # 随机金额
        gross_amount = round(random.uniform(50, 500), 2)
        discount_amount = round(gross_amount * random.uniform(0, 0.15), 2) if random.random() < 0.3 else 0
        net_amount = round(gross_amount - discount_amount, 2)
        
        # 渠道和支付方式
        channel = random.choice(["dine_in", "takeout", "delivery"])
        payment_method = random.choice(["cash", "alipay", "wechat", "bank"])
        
        order = {
            "order_no": f"TEST{order_counter + i:06d}",
            "biz_date": biz_date.strftime("%Y-%m-%d"),
            "gross_amount": gross_amount,
            "discount_amount": discount_amount,
            "net_amount": net_amount,
            "channel": channel,
            "payment_method": payment_method,
            "customer_name": random_name() if random.random() > 0.3 else "",
            "customer_phone": random_phone() if random.random() > 0.7 else "",
            "table_no": f"T{random.randint(1, 30):02d}" if channel == "dine_in" else "",
        }
        
        orders.append(order)
    
    df = pd.DataFrame(orders)
    print(f"  ✅ 生成了 {len(df)} 条订单记录")
    return df


def generate_expense_records_data(count: int = 30, start_date: date = None) -> pd.DataFrame:
    """
    生成费用记录导入测试数据
    
    必需字段：
    - expense_type_code: 费用科目编码（需在系统中存在）
    - biz_date: 业务日期 (YYYY-MM-DD)
    - amount: 金额
    
    可选字段：
    - payment_method: 支付方式 (cash|alipay|wechat|bank)
    - vendor: 供应商
    - description: 描述
    - invoice_no: 发票号
    """
    print(f"💰 生成 {count} 条费用记录数据...")
    
    if start_date is None:
        start_date = date.today() - timedelta(days=30)
    
    # 常见费用科目编码（需要与系统中的数据匹配）
    expense_type_codes = [
        "EXP_MATERIAL_FOOD",   # 食材采购
        "EXP_MATERIAL_BEV",    # 饮料采购
        "EXP_LABOR_SALARY",    # 员工工资
        "EXP_RENT",            # 租金
        "EXP_UTILITIES_ELEC",  # 电费
        "EXP_UTILITIES_WATER", # 水费
        "EXP_MARKETING_AD",    # 广告费用
    ]
    
    vendors = ["北京XX供应商", "上海YY食材公司", "广州ZZ批发市场", "深圳AA配送中心", "成都BB采购站"]
    
    expenses = []
    
    for i in range(count):
        # 随机日期
        days_offset = random.randint(0, 29)
        biz_date = start_date + timedelta(days=days_offset)
        
        # 随机费用类型
        expense_type_code = random.choice(expense_type_codes)
        
        # 根据费用类型设置合理的金额范围
        if "SALARY" in expense_type_code:
            amount = round(random.uniform(3000, 8000), 2)
        elif "RENT" in expense_type_code:
            amount = round(random.uniform(10000, 30000), 2)
        elif "MATERIAL" in expense_type_code:
            amount = round(random.uniform(500, 3000), 2)
        else:
            amount = round(random.uniform(100, 1000), 2)
        
        expense = {
            "expense_type_code": expense_type_code,
            "biz_date": biz_date.strftime("%Y-%m-%d"),
            "amount": amount,
            "payment_method": random.choice(["cash", "alipay", "wechat", "bank"]),
            "vendor": random.choice(vendors) if random.random() > 0.2 else "",
            "description": f"测试费用-{expense_type_code}-{i+1}",
            "invoice_no": f"INV{random.randint(100000, 999999)}" if random.random() > 0.5 else "",
        }
        
        expenses.append(expense)
    
    df = pd.DataFrame(expenses)
    print(f"  ✅ 生成了 {len(df)} 条费用记录")
    return df


def generate_stores_data(count: int = 5) -> pd.DataFrame:
    """
    生成门店信息导入测试数据
    
    必需字段：
    - code: 门店编码（唯一）
    - name: 门店名称
    
    可选字段：
    - address: 地址
    - phone: 电话
    - contact_person: 联系人
    - business_hours: 营业时间
    - area_sqm: 面积（平方米）
    - is_active: 是否启用 (true|false)
    """
    print(f"🏪 生成 {count} 个门店数据...")
    
    stores = []
    
    for i in range(count):
        landmark = random.choice(BJ_LANDMARKS)
        code = f"TEST_S{i+1:03d}"
        
        store = {
            "code": code,
            "name": f"测试{landmark}店",
            "address": random_address(),
            "phone": random_phone(),
            "contact_person": random_name(),
            "business_hours": "10:00-22:00",
            "area_sqm": random.randint(100, 250),
            "is_active": random.choice([True, True, True, False]),  # 75%启用
            "remark": f"测试门店 {i+1}",
        }
        
        stores.append(store)
    
    df = pd.DataFrame(stores)
    print(f"  ✅ 生成了 {len(df)} 个门店")
    return df


def generate_expense_types_data(count: int = 10) -> pd.DataFrame:
    """
    生成费用科目导入测试数据
    
    必需字段：
    - type_code: 科目编码（唯一）
    - name: 科目名称
    - level: 层级 (1|2)
    - category: 分类 (cost|expense|tax)
    
    可选字段：
    - parent_code: 父科目编码（二级科目必需）
    - description: 描述
    - is_active: 是否启用 (true|false)
    """
    print(f"📂 生成 {count} 个费用科目数据...")
    
    expense_types = []
    
    # 生成一级科目
    level1_count = count // 2
    for i in range(level1_count):
        expense_type = {
            "type_code": f"TEST_EXP_L1_{i+1:02d}",
            "name": f"测试一级科目{i+1}",
            "level": 1,
            "category": random.choice(["cost", "expense", "tax"]),
            "parent_code": "",
            "description": f"测试一级费用科目 {i+1}",
            "is_active": True,
            "sort_order": i + 1,
        }
        expense_types.append(expense_type)
    
    # 生成二级科目
    level2_count = count - level1_count
    for i in range(level2_count):
        parent_idx = i % level1_count
        parent_code = f"TEST_EXP_L1_{parent_idx+1:02d}"
        
        expense_type = {
            "type_code": f"TEST_EXP_L2_{i+1:02d}",
            "name": f"测试二级科目{i+1}",
            "level": 2,
            "category": random.choice(["cost", "expense"]),
            "parent_code": parent_code,
            "description": f"测试二级费用科目 {i+1}，属于 {parent_code}",
            "is_active": True,
            "sort_order": i + 1,
        }
        expense_types.append(expense_type)
    
    df = pd.DataFrame(expense_types)
    print(f"  ✅ 生成了 {len(df)} 个费用科目（{level1_count}个一级，{level2_count}个二级）")
    return df


def save_data_files(data_dict: dict):
    """保存数据文件（Excel和CSV两种格式）"""
    print(f"\n💾 保存数据文件到 {OUTPUT_DIR}...")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for name, df in data_dict.items():
        # 保存 Excel
        excel_path = OUTPUT_DIR / f"{name}.xlsx"
        df.to_excel(excel_path, index=False, engine="openpyxl")
        print(f"  ✅ {excel_path.name}")
        
        # 保存 CSV
        csv_path = OUTPUT_DIR / f"{name}.csv"
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")  # utf-8-sig 支持中文
        print(f"  ✅ {csv_path.name}")


def generate_readme():
    """生成使用说明文档"""
    readme_content = """# 数据导入测试文件说明

## 文件列表

### 1. 订单数据 (orders_import_test)
- **用途**: 测试订单导入功能
- **记录数**: 50条
- **格式**: Excel (.xlsx) 和 CSV (.csv)
- **必需字段**:
  - `order_no`: 订单号（唯一）
  - `biz_date`: 业务日期 (格式: YYYY-MM-DD)
  - `gross_amount`: 总金额
  - `discount_amount`: 折扣金额
  - `net_amount`: 实收金额
- **可选字段**: channel, payment_method, customer_name, customer_phone, table_no
- **导入要求**: 需要指定门店ID

### 2. 费用记录 (expense_records_import_test)
- **用途**: 测试费用记录导入功能
- **记录数**: 30条
- **格式**: Excel (.xlsx) 和 CSV (.csv)
- **必需字段**:
  - `expense_type_code`: 费用科目编码（需在系统中存在）
  - `biz_date`: 业务日期 (格式: YYYY-MM-DD)
  - `amount`: 金额
- **可选字段**: payment_method, vendor, description, invoice_no
- **导入要求**: 需要指定门店ID
- **注意**: 费用科目编码必须与系统中的数据匹配，参考：
  - EXP_MATERIAL_FOOD (食材采购)
  - EXP_MATERIAL_BEV (饮料采购)
  - EXP_LABOR_SALARY (员工工资)
  - EXP_RENT (租金)
  - EXP_UTILITIES_ELEC (电费)
  - EXP_UTILITIES_WATER (水费)
  - EXP_MARKETING_AD (广告费用)

### 3. 门店信息 (stores_import_test)
- **用途**: 测试门店导入功能
- **记录数**: 5条
- **格式**: Excel (.xlsx) 和 CSV (.csv)
- **必需字段**:
  - `code`: 门店编码（唯一）
  - `name`: 门店名称
- **可选字段**: address, phone, contact_person, business_hours, area_sqm, is_active
- **注意**: 门店编码不能与现有门店重复

### 4. 费用科目 (expense_types_import_test)
- **用途**: 测试费用科目导入功能
- **记录数**: 10条（5个一级科目，5个二级科目）
- **格式**: Excel (.xlsx) 和 CSV (.csv)
- **必需字段**:
  - `type_code`: 科目编码（唯一）
  - `name`: 科目名称
  - `level`: 层级 (1 或 2)
  - `category`: 分类 (cost|expense|tax)
- **可选字段**: parent_code, description, is_active, sort_order
- **注意**: 
  - 二级科目的 parent_code 必须指向已存在的一级科目
  - 科目编码不能与现有科目重复

## 使用方法

### 通过前端页面导入
1. 登录系统
2. 进入"数据导入"页面
3. 选择导入类型（订单数据、费用记录、门店信息、费用科目）
4. 选择对应的测试文件（.xlsx 或 .csv）
5. 如果是订单或费用记录，需要选择门店
6. 点击"导入数据"按钮
7. 等待处理完成，查看导入结果

### 通过API导入
```bash
# 1. 登录获取token
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{"username": "admin", "password": "Admin@123"}'

# 2. 创建导入任务（上传文件）
curl -X POST "http://localhost:8000/api/v1/import-jobs" \\
  -H "Authorization: Bearer <token>" \\
  -F "file=@services/api/test_data/orders_import_test.xlsx" \\
  -F "target_type=orders" \\
  -F "store_id=1" \\
  -F "job_name=测试订单导入"

# 3. 执行导入任务
curl -X POST "http://localhost:8000/api/v1/import-jobs/{job_id}/run" \\
  -H "Authorization: Bearer <token>"

# 4. 查看任务结果
curl -X GET "http://localhost:8000/api/v1/import-jobs/{job_id}" \\
  -H "Authorization: Bearer <token>"
```

## 测试建议

### 正常流程测试
1. 先导入"门店信息"，创建测试门店
2. 再导入"费用科目"（可选，系统已有默认科目）
3. 使用新创建的门店ID导入"订单数据"
4. 使用新创建的门店ID导入"费用记录"

### 异常情况测试
1. **重复导入**: 尝试导入相同订单号的订单，验证幂等性
2. **缺少必填字段**: 删除某些必填列后导入，验证校验逻辑
3. **错误格式**: 修改日期或金额格式，验证数据转换
4. **不存在的关联数据**: 使用不存在的费用科目编码，验证关联校验
5. **大数据量**: 生成更多数据（修改脚本中的count参数），验证性能

## 生成新数据

如需生成新的测试数据，运行：
```bash
cd services/api
python tooling/api/generate_import_test_data.py
```

可修改脚本中的参数：
- `generate_orders_data(count=50)` - 订单数量
- `generate_expense_records_data(count=30)` - 费用记录数量
- `generate_stores_data(count=5)` - 门店数量
- `generate_expense_types_data(count=10)` - 费用科目数量
"""
    
    readme_path = OUTPUT_DIR / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"  ✅ {readme_path.name}")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 开始生成数据导入测试文件...")
    print("="*70 + "\n")
    
    try:
        # 1. 生成各类数据
        orders_df = generate_orders_data(count=50)
        expense_records_df = generate_expense_records_data(count=30)
        stores_df = generate_stores_data(count=5)
        expense_types_df = generate_expense_types_data(count=10)
        
        # 2. 保存文件
        data_dict = {
            "orders_import_test": orders_df,
            "expense_records_import_test": expense_records_df,
            "stores_import_test": stores_df,
            "expense_types_import_test": expense_types_df,
        }
        
        save_data_files(data_dict)
        
        # 3. 生成说明文档
        generate_readme()
        
        print("\n" + "="*70)
        print("✅ 测试文件生成完成！")
        print("="*70)
        print(f"\n📁 文件位置: {OUTPUT_DIR.absolute()}")
        print(f"📄 共生成 {len(data_dict) * 2} 个数据文件 + 1 个说明文档")
        print("\n💡 提示: 查看 README.md 了解如何使用这些测试文件\n")
        
    except Exception as e:
        print(f"\n❌ 生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

