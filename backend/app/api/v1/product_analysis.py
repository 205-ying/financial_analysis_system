"""
菜品销售分析 API

提供菜品销量排行、品类分布、毛利贡献、ABC分类、门店交叉分析等接口。
"""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, check_permission
from app.models.user import User
from app.schemas.common import Response
from app.schemas.product_analysis import (
    ProductSalesRankingItem,
    CategorySalesItem,
    ProductProfitItem,
    ProductABCItem,
    ProductStoreCrossItem,
)
from app.services import product_analysis_service
from app.services.audit_log_service import log_audit
from app.services.data_scope_service import filter_stores_by_access

router = APIRouter()


@router.get("/sales-ranking", response_model=Response[List[ProductSalesRankingItem]])
async def get_sales_ranking(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    top_n: int = Query(20, ge=1, le=100, description="返回Top N条记录"),
    sort_by: str = Query("quantity", description="排序字段: quantity 或 revenue"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取菜品销量排行榜

    权限: product_analysis:view
    """
    await check_permission(current_user, "product_analysis:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await product_analysis_service.get_product_sales_ranking(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        accessible_store_ids=accessible_store_ids,
        top_n=top_n,
        sort_by=sort_by,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="view_product_sales_ranking",
        request=request,
        resource_type="product_analysis",
        detail={
            "start_date": start_date,
            "end_date": end_date,
            "store_id": store_id,
            "top_n": top_n,
            "sort_by": sort_by,
            "record_count": len(data),
        },
    )

    return Response(code=200, message="查询成功", data=data)


@router.get("/category-distribution", response_model=Response[List[CategorySalesItem]])
async def get_category_distribution(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取品类销售占比分布

    权限: product_analysis:view
    """
    await check_permission(current_user, "product_analysis:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await product_analysis_service.get_category_sales_distribution(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        accessible_store_ids=accessible_store_ids,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="view_category_distribution",
        request=request,
        resource_type="product_analysis",
        detail={
            "start_date": start_date,
            "end_date": end_date,
            "store_id": store_id,
            "record_count": len(data),
        },
    )

    return Response(code=200, message="查询成功", data=data)


@router.get("/profit-contribution", response_model=Response[List[ProductProfitItem]])
async def get_profit_contribution(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    top_n: int = Query(20, ge=1, le=100, description="返回Top N条记录"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取菜品毛利贡献排行

    权限: product_analysis:view
    """
    await check_permission(current_user, "product_analysis:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await product_analysis_service.get_product_profit_contribution(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        accessible_store_ids=accessible_store_ids,
        top_n=top_n,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="view_profit_contribution",
        request=request,
        resource_type="product_analysis",
        detail={
            "start_date": start_date,
            "end_date": end_date,
            "store_id": store_id,
            "top_n": top_n,
            "record_count": len(data),
        },
    )

    return Response(code=200, message="查询成功", data=data)


@router.get("/abc-classification", response_model=Response[List[ProductABCItem]])
async def get_abc_classification(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取菜品ABC分类

    A类(累计占比≤70%): 核心菜品
    B类(累计占比≤90%): 重要菜品
    C类(累计占比>90%): 长尾菜品

    权限: product_analysis:view
    """
    await check_permission(current_user, "product_analysis:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await product_analysis_service.get_product_abc_classification(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        accessible_store_ids=accessible_store_ids,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="view_abc_classification",
        request=request,
        resource_type="product_analysis",
        detail={
            "start_date": start_date,
            "end_date": end_date,
            "store_id": store_id,
            "record_count": len(data),
        },
    )

    return Response(code=200, message="查询成功", data=data)


@router.get("/product-store-cross", response_model=Response[List[ProductStoreCrossItem]])
async def get_product_store_cross(
    request: Request,
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: int | None = Query(None, description="门店ID（为空表示全部门店）"),
    top_n: int = Query(10, ge=1, le=50, description="Top N菜品"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    获取菜品-门店交叉分析

    展示Top N菜品在各门店的销售表现。

    权限: product_analysis:view
    """
    await check_permission(current_user, "product_analysis:view", db)

    accessible_store_ids = await filter_stores_by_access(db, current_user, store_id)

    data = await product_analysis_service.get_product_store_cross_analysis(
        db=db,
        start_date=date.fromisoformat(start_date),
        end_date=date.fromisoformat(end_date),
        accessible_store_ids=accessible_store_ids,
        top_n=top_n,
    )

    await log_audit(
        db=db,
        user=current_user,
        action="view_product_store_cross",
        request=request,
        resource_type="product_analysis",
        detail={
            "start_date": start_date,
            "end_date": end_date,
            "store_id": store_id,
            "top_n": top_n,
            "record_count": len(data),
        },
    )

    return Response(code=200, message="查询成功", data=data)
