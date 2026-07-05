# pyright: reportAny=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false

"""
性能基线采集脚本（EXPLAIN ANALYZE + 索引审计）

用途：
- 对核心查询采集 EXPLAIN ANALYZE 结果
- 导出关键表索引清单
- 生成可留档、可对比的 Markdown 报告

使用方法：
cd services/api
python tooling/api/maintenance/performance_baseline.py --start-date 2026-01-01 --end-date 2026-01-31
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

from sqlalchemy import text


class BaselineArgs(NamedTuple):
    start_date: str | None
    end_date: str | None
    store_id: int | None
    expense_type_id: int | None
    output: str | None


class QuerySpec(NamedTuple):
    name: str
    sql: str


CORE_QUERIES: list[QuerySpec] = [
    QuerySpec(
        name="orders_list",
        sql="""
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT oh.id, oh.order_no, oh.store_id, oh.channel, oh.net_amount, oh.order_time, oh.remark, oh.status
FROM order_headers oh
LEFT JOIN stores s ON oh.store_id = s.id
WHERE (:store_id::int IS NULL OR oh.store_id = :store_id)
  AND (:channel::text IS NULL OR oh.channel = :channel)
  AND (:start_date::date IS NULL OR DATE(oh.order_time) >= :start_date)
  AND (:end_date::date IS NULL OR DATE(oh.order_time) <= :end_date)
ORDER BY oh.order_time DESC
LIMIT 100;
""",
    ),
    QuerySpec(
        name="expense_records_list",
        sql="""
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT er.id, er.store_id, er.expense_type_id, er.biz_date, er.amount, er.remark
FROM expense_records er
LEFT JOIN stores s ON er.store_id = s.id
LEFT JOIN expense_types et ON er.expense_type_id = et.id
WHERE (:store_id::int IS NULL OR er.store_id = :store_id)
  AND (:expense_type_id::int IS NULL OR er.expense_type_id = :expense_type_id)
  AND (:start_date::date IS NULL OR er.biz_date >= :start_date)
  AND (:end_date::date IS NULL OR er.biz_date <= :end_date)
ORDER BY er.biz_date DESC
LIMIT 100;
""",
    ),
    QuerySpec(
        name="kpi_summary_aggregate",
        sql="""
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT kds.store_id,
       SUM(kds.revenue) AS total_revenue,
       SUM(kds.order_count) AS total_orders,
       AVG(kds.avg_order_value) AS avg_order_value
FROM kpi_daily_stores kds
WHERE (:store_id::int IS NULL OR kds.store_id = :store_id)
  AND (:start_date::date IS NULL OR kds.biz_date >= :start_date)
  AND (:end_date::date IS NULL OR kds.biz_date <= :end_date)
GROUP BY kds.store_id
ORDER BY total_revenue DESC;
""",
    ),
]

INDEX_AUDIT_SQL = """
SELECT schemaname, tablename, indexname, indexdef
FROM pg_indexes
WHERE tablename IN ('order_headers', 'expense_records', 'kpi_daily_stores', 'user_store_permissions')
ORDER BY tablename, indexname;
"""


def parse_args() -> BaselineArgs:
    parser = argparse.ArgumentParser(description="采集性能基线报告")
    _ = parser.add_argument("--start-date", type=str, default=None, help="开始日期，格式 YYYY-MM-DD")
    _ = parser.add_argument("--end-date", type=str, default=None, help="结束日期，格式 YYYY-MM-DD")
    _ = parser.add_argument("--store-id", type=int, default=None, help="门店ID（可选）")
    _ = parser.add_argument("--expense-type-id", type=int, default=None, help="费用类型ID（可选）")
    _ = parser.add_argument("--output", type=str, default=None, help="输出文件路径（可选）")
    parsed = parser.parse_args()
    return BaselineArgs(
        start_date=parsed.start_date,
        end_date=parsed.end_date,
        store_id=parsed.store_id,
        expense_type_id=parsed.expense_type_id,
        output=parsed.output,
    )


def _render_explain_block(lines: list[str]) -> str:
    return "\n".join(lines)


async def collect_baseline(args: BaselineArgs) -> Path:
    now = datetime.now()
    default_output = Path("logs") / f"performance_baseline_{now.strftime('%Y%m%d_%H%M%S')}.md"
    output_path = Path(args.output) if args.output else default_output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report_lines: list[str] = [
        "# 性能基线报告",
        "",
        f"- 生成时间：{now.strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 开始日期：{args.start_date or '未指定'}",
        f"- 结束日期：{args.end_date or '未指定'}",
        f"- 门店ID：{args.store_id if args.store_id is not None else '未指定'}",
        f"- 费用类型ID：{args.expense_type_id if args.expense_type_id is not None else '未指定'}",
        "",
        "## EXPLAIN ANALYZE 结果",
        "",
    ]

    database_module = importlib.import_module("app.core.database")
    async_session_local = database_module.AsyncSessionLocal

    async with async_session_local() as session:
        params = {
            "start_date": args.start_date,
            "end_date": args.end_date,
            "store_id": args.store_id,
            "channel": None,
            "expense_type_id": args.expense_type_id,
        }

        for query in CORE_QUERIES:
            result = await session.execute(text(query.sql), params)
            explain_lines = [row[0] for row in result.fetchall()]

            report_lines.extend(
                [
                    f"### {query.name}",
                    "",
                    "```text",
                    _render_explain_block(explain_lines),
                    "```",
                    "",
                ]
            )

        report_lines.extend(["## 索引审计", ""])
        index_result = await session.execute(text(INDEX_AUDIT_SQL))
        index_rows = index_result.fetchall()

        report_lines.extend(
            [
                "| Schema | Table | Index | Definition |",
                "|---|---|---|---|",
            ]
        )
        for row in index_rows:
            schemaname, tablename, indexname, indexdef = row
            report_lines.append(
                f"| {schemaname} | {tablename} | {indexname} | {str(indexdef).replace('|', '\\|')} |"
            )

    report_lines.extend(
        [
            "",
            "## 使用建议",
            "",
            "- 将本报告纳入版本库（或归档目录），用于发布前后对比。",
            "- 对比重点：执行时间、是否命中索引、是否出现顺序扫描放大。",
            "- 如出现性能回退，优先检查筛选条件、索引覆盖和统计信息。",
        ]
    )

    _ = output_path.write_text("\n".join(report_lines), encoding="utf-8")
    return output_path


async def main() -> None:
    args = parse_args()
    output_path = await collect_baseline(args)
    print("✅ 性能基线采集完成")
    print(f"📄 报告路径: {output_path}")


if __name__ == "__main__":
    asyncio.run(main())

