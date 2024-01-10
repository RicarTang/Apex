from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise.transactions import in_transaction
from ..db.models import Routes, RouteMeta
from ..schemas import ResultResponse, menu
from ..core.security import (
    check_jwt_auth,
    get_current_user as current_user,
)

router = APIRouter()


@router.get(
    "/list",
    summary="菜单列表",
)
async def menu_list(
    # username: Optional[str] = Query(default=None, description="用户名", alias="userName"),
    # status: Optional[str] = Query(default=None, description="用户状态"),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取菜单列表"""
    filters = {}
    if begin_time:
        begin_time = datetime.strptime(begin_time, "%Y-%m-%d")
        filters["created_at__gte"] = begin_time
    if end_time:
        end_time = datetime.strptime(end_time, "%Y-%m-%d")
        filters["created_at__lte"] = end_time
    if begin_time and end_time:
        filters["created_at__range"] = (
            begin_time,
            end_time,
        )
    query = Routes.filter(**filters)
    menu_list = await query.prefetch_related("children__route_meta", "route_meta")
    total = await query.count()
    # return ResultResponse[]


@router.get(
    "/treeselect",
    summary="查询菜单树结构",
    response_model=ResultResponse[List[menu.TreeSelectTo]],
)
async def get_treeselect():
    """查询菜单树结构"""
    route_list = await Routes.filter(parent_id__isnull=True).prefetch_related(
        "children__route_meta", "route_meta"
    )
    return ResultResponse[List[menu.TreeSelectTo]](result=route_list)


@router.post(
    "/addMenu",
    summary="添加菜单",
    response_model=ResultResponse[menu.AddMenuTo],
)
async def add_menu(body: menu.AddMenuIn):
    """添加前端路由菜单"""
    async with in_transaction():
        # 路由
        route = await Routes.create(
            **body.model_dump(exclude_unset=True, exclude=["meta"])
        )
        # 添加路由meta
        await RouteMeta.create(**body.meta.model_dump(exclude_unset=True), route=route)
        result = (
            await Routes.filter(id=route.id)
            .prefetch_related("children__meta", "meta")
            .first()
        )
    return ResultResponse[menu.AddMenuTo](result=result)
