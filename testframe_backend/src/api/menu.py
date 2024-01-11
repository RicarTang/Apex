from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query
from tortoise.transactions import in_transaction
from ..db.models import Routes, RouteMeta
from ..schemas import ResultResponse, menu
from ..utils.exceptions.menu import MenuNotExistException

router = APIRouter()


@router.get(
    "/list",
    summary="菜单列表",
    response_model=ResultResponse[menu.MenuListTo],
)
async def menu_list(
    menuname: Optional[str] = Query(
        default=None, description="菜单label", alias="menuName"
    ),
    status: Optional[str] = Query(default=None, description="菜单状态"),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取菜单列表"""
    filters = {}
    if menuname:
        filters["route_meta__title__icontains"] = menuname
    if status:
        filters["status"] = status
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
    query = Routes.filter(**filters, parent_id__isnull=True)
    menu_list = (
        await query.prefetch_related("children__route_meta", "route_meta")
        .offset(limit * (page - 1))
        .limit(limit)
        .all()
    )
    total = await query.count()
    return ResultResponse[menu.MenuListTo](
        result=menu.MenuListTo(data=menu_list, page=page, limit=limit, total=total)
    )


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
    "/add",
    summary="添加菜单",
    response_model=ResultResponse[menu.MenuTo],
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
    return ResultResponse[menu.MenuTo](result=result)


@router.delete(
    "/{menu_id}",
    summary="删除菜单",
    response_model=ResultResponse[None],
)
async def del_menu(menu_id: int):
    """删除菜单"""
    delete_count = await Routes.filter(id=menu_id).delete()
    if not delete_count:
        raise MenuNotExistException
    return ResultResponse[None](message="successful deleted menu!")
