from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query
from tortoise.transactions import in_transaction
from tortoise.query_utils import Prefetch

from ...schemas.management import menu
from ...db.models import Routes, RouteMeta
from ...schemas import ResultResponse
from ...utils.exceptions.menu import MenuNotExistException
from ...utils.log_util import log

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
    if filters:
        query = Routes.filter(parent_id__isnull=True)
    else:
        query = Routes.filter(**filters,parent_id__isnull=True)
    menu_list = (
        await query.prefetch_related(
            Prefetch(
                "children",
                queryset=Routes.filter(**filters).prefetch_related(),
            ),
            "children__route_meta",
            "route_meta",
        )
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
        # 添加路由meta
        route_meta = await RouteMeta.create(**body.meta.model_dump(exclude_unset=True))
        # 路由
        route = await Routes.create(
            **body.model_dump(exclude_unset=True, exclude=["meta"]),
            route_meta=route_meta,
        )

        return ResultResponse[menu.MenuTo](result=route)


@router.get(
    "/{menu_id}",
    summary="查询菜单",
    response_model=ResultResponse[menu.MenuTo],
)
async def get_menu(menu_id: int):
    """查询菜单"""
    query = (
        await Routes.filter(id=menu_id)
        .prefetch_related("children__route_meta", "route_meta")
        .first()
    )
    if not query:
        raise MenuNotExistException
    return ResultResponse[menu.MenuTo](result=query)


@router.put(
    "/{menu_id}",
    summary="更新菜单",
    response_model=ResultResponse[None],
)
async def update_menu(menu_id: int, body: menu.MenuUpdateIn):
    """更新菜单"""
    query = (
        await Routes.filter(id=menu_id)
        .prefetch_related("children__route_meta", "route_meta")
        .first()
    )
    if not query:
        raise MenuNotExistException
    # 更新关联模型字段
    if body.meta.title:
        query.route_meta.title = body.meta.title
    if body.meta.icon:
        query.route_meta.icon = body.meta.icon
    if body.meta.no_cache:
        query.route_meta.no_cache = body.meta.no_cache
    if body.meta.link:
        query.route_meta.link = body.meta.link
    async with in_transaction():
        # 更新多个字段
        query.update_from_dict(body.model_dump(exclude_unset=True))
        # 修改关联模型数据需要save
        await query.route_meta.save()
        await query.save()
    return ResultResponse[None](message="successful updated menu!")


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
