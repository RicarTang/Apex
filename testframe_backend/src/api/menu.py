from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from ..core.security import (
    create_access_token,
    check_jwt_auth,
)
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
