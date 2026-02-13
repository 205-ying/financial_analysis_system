"""
数据导入功能验证脚本

快速验证导入功能的核心组件
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
backend_dir = Path(__file__).resolve().parents[3] / "backend"
sys.path.insert(0, str(backend_dir))

from app.models.import_job import (
    DataImportJob,
    DataImportJobError,
    ImportSourceType,
    ImportTargetType,
    ImportJobStatus,
)
from app.schemas.import_job import ImportJobCreate, ImportJobOut
from app.services.import_service import ImportService


async def test_models():
    """测试模型定义"""
    print("✅ 测试模型定义...")
    
    job = DataImportJob(
        job_name="测试任务",
        source_type=ImportSourceType.CSV,
        target_type=ImportTargetType.ORDERS,
        status=ImportJobStatus.PENDING,
        file_name="test.csv",
        file_path="/tmp/test.csv",
        total_rows=0,
        success_rows=0,
        fail_rows=0,
    )
    
    print(f"  - DataImportJob: {job}")
    print(f"  - 状态: {job.status.value}")
    print(f"  - 源类型: {job.source_type.value}")
    print(f"  - 目标类型: {job.target_type.value}")


def test_schemas():
    """测试 Schema 定义"""
    print("\n✅ 测试 Schema 定义...")
    
    # 创建请求
    create_data = ImportJobCreate(
        job_name="订单导入测试",
        target_type=ImportTargetType.ORDERS,
        store_id=1,
    )
    print(f"  - ImportJobCreate: {create_data.model_dump()}")
    
    # 输出响应（模拟）
    job_out = ImportJobOut(
        id=1,
        job_name="订单导入测试",
        source_type=ImportSourceType.CSV,
        target_type=ImportTargetType.ORDERS,
        status=ImportJobStatus.PENDING,
        file_name="orders.csv",
        total_rows=0,
        success_rows=0,
        fail_rows=0,
        error_report_path=None,
        created_by_id=1,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    print(f"  - ImportJobOut: {job_out.model_dump_json(indent=2)}")


def test_service_methods():
    """测试 Service 方法签名"""
    print("\n✅ 测试 Service 方法...")
    
    # 检查方法存在
    methods = [
        "create_job",
        "run_job",
        "list_jobs",
        "get_job_detail",
        "list_job_errors",
        "build_error_report",
    ]
    
    for method in methods:
        if hasattr(ImportService, method):
            print(f"  ✓ {method}")
        else:
            print(f"  ✗ {method} 未找到")


def main():
    """主函数"""
    print("=" * 60)
    print("数据导入功能验证")
    print("=" * 60)
    
    asyncio.run(test_models())
    test_schemas()
    test_service_methods()
    
    print("\n" + "=" * 60)
    print("✅ 所有组件验证完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
