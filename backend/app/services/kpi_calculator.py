"""
KPI 计算服务
使用 SQL 聚合进行高性能计算,避免大量数据传输
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, func, and_, case, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import OrderHeader
from app.models.expense import ExpenseRecord, ExpenseType
from app.models.kpi import KpiDailyStore
from app.models.store import Store


class KpiCalculator:
    """KPI 计算器"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def rebuild_daily_kpi(
        self,
        start_date: date,
        end_date: date,
        store_id: Optional[int] = None
    ) -> Tuple[int, int, int]:
        """
        重建日指标数据（upsert 模式）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            store_id: 可选的门店ID，如果不提供则计算所有门店
        
        Returns:
            (affected_dates, affected_stores, total_records)
        """
        # 获取需要计算的门店列表
        store_query = select(Store.id).where(Store.status == "active")
        if store_id:
            store_query = store_query.where(Store.id == store_id)
        
        store_result = await self.db.execute(store_query)
        store_ids = [row[0] for row in store_result.all()]
        
        if not store_ids:
            return (0, 0, 0)
        
        # 生成日期范围
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            from datetime import timedelta
            current += timedelta(days=1)
        
        total_records = 0
        
        # 对每个门店和日期组合计算KPI
        for sid in store_ids:
            for biz_date in dates:
                await self._calculate_and_upsert_kpi(sid, biz_date)
                total_records += 1
        
        return (len(dates), len(store_ids), total_records)
    
    async def _calculate_and_upsert_kpi(self, store_id: int, biz_date: date):
        """
        计算并更新单个门店单日的KPI数据
        使用 SQL 聚合保证性能
        """
        # 1. 聚合订单数据
        order_stats = await self._aggregate_orders(store_id, biz_date)
        
        # 2. 聚合费用数据
        cost_stats = await self._aggregate_costs(store_id, biz_date)
        
        # 3. 计算利润指标
        net_revenue = order_stats["revenue_total"] - order_stats["refund_amount"]
        cost_total = sum([
            cost_stats["cost_material"],
            cost_stats["cost_labor"],
            cost_stats["cost_rent"],
            cost_stats["cost_utilities"],
            cost_stats["cost_other"]
        ])
        profit_gross = net_revenue - cost_stats["cost_material"]
        profit_net = net_revenue - cost_total
        
        # 4. 查找是否已存在记录
        existing = await self.db.execute(
            select(KpiDailyStore).where(
                and_(
                    KpiDailyStore.store_id == store_id,
                    KpiDailyStore.biz_date == biz_date
                )
            )
        )
        kpi_record = existing.scalar_one_or_none()
        
        # 5. Upsert 操作
        if kpi_record:
            # 更新现有记录
            kpi_record.revenue_total = order_stats["revenue_total"]
            kpi_record.revenue_dine_in = order_stats["revenue_dine_in"]
            kpi_record.revenue_takeout = order_stats["revenue_takeout"]
            kpi_record.revenue_delivery = order_stats["revenue_delivery"]
            kpi_record.refund_amount = order_stats["refund_amount"]
            kpi_record.net_revenue = net_revenue
            kpi_record.order_count = order_stats["order_count"]
            kpi_record.customer_count = order_stats["customer_count"]
            kpi_record.cost_material = cost_stats["cost_material"]
            kpi_record.cost_labor = cost_stats["cost_labor"]
            kpi_record.cost_rent = cost_stats["cost_rent"]
            kpi_record.cost_utilities = cost_stats["cost_utilities"]
            kpi_record.cost_other = cost_stats["cost_other"]
            kpi_record.cost_total = cost_total
            kpi_record.profit_gross = profit_gross
            kpi_record.profit_net = profit_net
        else:
            # 插入新记录
            kpi_record = KpiDailyStore(
                biz_date=biz_date,
                store_id=store_id,
                revenue_total=order_stats["revenue_total"],
                revenue_dine_in=order_stats["revenue_dine_in"],
                revenue_takeout=order_stats["revenue_takeout"],
                revenue_delivery=order_stats["revenue_delivery"],
                refund_amount=order_stats["refund_amount"],
                net_revenue=net_revenue,
                order_count=order_stats["order_count"],
                customer_count=order_stats["customer_count"],
                cost_material=cost_stats["cost_material"],
                cost_labor=cost_stats["cost_labor"],
                cost_rent=cost_stats["cost_rent"],
                cost_utilities=cost_stats["cost_utilities"],
                cost_other=cost_stats["cost_other"],
                cost_total=cost_total,
                profit_gross=profit_gross,
                profit_net=profit_net
            )
            self.db.add(kpi_record)
        
        await self.db.commit()
    
    async def _aggregate_orders(self, store_id: int, biz_date: date) -> dict:
        """
        使用 SQL 聚合订单数据（一次查询获取所有指标）
        """
        # 构建 SQL 聚合查询
        query = select(
            # 总营收（已完成订单）
            func.coalesce(
                func.sum(
                    case(
                        (OrderHeader.status == "completed", OrderHeader.final_amount),
                        else_=Decimal("0")
                    )
                ),
                Decimal("0")
            ).label("revenue_total"),
            # 堂食营收
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                OrderHeader.status == "completed",
                                OrderHeader.channel == "dine-in"
                            ),
                            OrderHeader.final_amount
                        ),
                        else_=Decimal("0")
                    )
                ),
                Decimal("0")
            ).label("revenue_dine_in"),
            # 外卖营收
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                OrderHeader.status == "completed",
                                OrderHeader.channel == "takeout"
                            ),
                            OrderHeader.final_amount
                        ),
                        else_=Decimal("0")
                    )
                ),
                Decimal("0")
            ).label("revenue_takeout"),
            # 配送营收
            func.coalesce(
                func.sum(
                    case(
                        (
                            and_(
                                OrderHeader.status == "completed",
                                OrderHeader.channel == "delivery"
                            ),
                            OrderHeader.final_amount
                        ),
                        else_=Decimal("0")
                    )
                ),
                Decimal("0")
            ).label("revenue_delivery"),
            # 退款金额
            func.coalesce(
                func.sum(OrderHeader.refund_amount),
                Decimal("0")
            ).label("refund_amount"),
            # 订单数（已完成）
            func.count(
                case(
                    (OrderHeader.status == "completed", OrderHeader.id),
                    else_=None
                )
            ).label("order_count"),
            # 客流量（简化：使用订单数）
            func.count(
                case(
                    (OrderHeader.status == "completed", OrderHeader.id),
                    else_=None
                )
            ).label("customer_count")
        ).where(
            and_(
                OrderHeader.store_id == store_id,
                OrderHeader.biz_date == biz_date
            )
        )
        
        result = await self.db.execute(query)
        row = result.first()
        
        if row:
            return {
                "revenue_total": row.revenue_total,
                "revenue_dine_in": row.revenue_dine_in,
                "revenue_takeout": row.revenue_takeout,
                "revenue_delivery": row.revenue_delivery,
                "refund_amount": row.refund_amount,
                "order_count": row.order_count,
                "customer_count": row.customer_count
            }
        else:
            return {
                "revenue_total": Decimal("0"),
                "revenue_dine_in": Decimal("0"),
                "revenue_takeout": Decimal("0"),
                "revenue_delivery": Decimal("0"),
                "refund_amount": Decimal("0"),
                "order_count": 0,
                "customer_count": 0
            }
    
    async def _aggregate_costs(self, store_id: int, biz_date: date) -> dict:
        """
        使用 SQL 聚合费用数据（按科目映射分类）
        只统计已审批的费用
        """
        # JOIN expense_record 和 expense_type，按 kpi_mapping 分组聚合
        query = select(
            ExpenseType.kpi_mapping,
            func.sum(ExpenseRecord.amount).label("total_amount")
        ).select_from(ExpenseRecord).join(
            ExpenseType,
            ExpenseRecord.expense_type_id == ExpenseType.id
        ).where(
            and_(
                ExpenseRecord.store_id == store_id,
                ExpenseRecord.biz_date == biz_date,
                ExpenseRecord.status == "approved"  # 只统计已审批的
            )
        ).group_by(ExpenseType.kpi_mapping)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        # 初始化成本字典
        costs = {
            "cost_material": Decimal("0"),
            "cost_labor": Decimal("0"),
            "cost_rent": Decimal("0"),
            "cost_utilities": Decimal("0"),
            "cost_other": Decimal("0")
        }
        
        # 按映射归类
        for row in rows:
            mapping = row.kpi_mapping
            amount = row.total_amount or Decimal("0")
            
            if mapping in costs:
                costs[mapping] += amount
            else:
                costs["cost_other"] += amount
        
        return costs
    
    async def get_daily_trend(
        self,
        start_date: date,
        end_date: date,
        store_id: Optional[int] = None,
        region: Optional[str] = None
    ) -> List[dict]:
        """
        获取日趋势数据（用于折线图）
        按日期聚合，可选按门店或区域筛选
        """
        # 基础查询
        query = select(
            KpiDailyStore.biz_date,
            func.sum(KpiDailyStore.net_revenue).label("revenue"),
            func.sum(KpiDailyStore.cost_total).label("cost"),
            func.sum(KpiDailyStore.profit_net).label("profit"),
            func.sum(KpiDailyStore.order_count).label("order_count")
        ).select_from(KpiDailyStore).where(
            and_(
                KpiDailyStore.biz_date >= start_date,
                KpiDailyStore.biz_date <= end_date
            )
        )
        
        # 筛选条件
        if store_id:
            query = query.where(KpiDailyStore.store_id == store_id)
        elif region:
            query = query.join(Store).where(Store.region == region)
        
        # 按日期分组并排序
        query = query.group_by(KpiDailyStore.biz_date).order_by(KpiDailyStore.biz_date)
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "date": row.biz_date,
                "revenue": float(row.revenue or 0),
                "cost": float(row.cost or 0),
                "profit": float(row.profit or 0),
                "order_count": row.order_count or 0
            }
            for row in rows
        ]
    
    async def get_store_comparison(
        self,
        start_date: date,
        end_date: date,
        region: Optional[str] = None
    ) -> List[dict]:
        """
        获取门店对比数据（用于柱状图）
        按门店聚合指定日期范围内的数据
        """
        # 基础查询（JOIN store 以获取门店信息）
        query = select(
            KpiDailyStore.store_id,
            Store.code.label("store_code"),
            Store.name.label("store_name"),
            func.sum(KpiDailyStore.net_revenue).label("revenue"),
            func.sum(KpiDailyStore.cost_total).label("cost"),
            func.sum(KpiDailyStore.profit_net).label("profit")
        ).select_from(KpiDailyStore).join(
            Store,
            KpiDailyStore.store_id == Store.id
        ).where(
            and_(
                KpiDailyStore.biz_date >= start_date,
                KpiDailyStore.biz_date <= end_date
            )
        )
        
        # 筛选条件
        if region:
            query = query.where(Store.region == region)
        
        # 按门店分组
        query = query.group_by(
            KpiDailyStore.store_id,
            Store.code,
            Store.name
        ).order_by(func.sum(KpiDailyStore.net_revenue).desc())
        
        result = await self.db.execute(query)
        rows = result.all()
        
        return [
            {
                "store_id": row.store_id,
                "store_code": row.store_code,
                "store_name": row.store_name,
                "revenue": float(row.revenue or 0),
                "cost": float(row.cost or 0),
                "profit": float(row.profit or 0),
                "profit_rate": float((row.profit / row.revenue * 100) if row.revenue else 0)
            }
            for row in rows
        ]
