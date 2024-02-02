from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status
from ..core.security import (
    create_access_token,
    check_jwt_auth,
    get_current_user as current_user,
)
from passlib.hash import md5_crypt
from tortoise.exceptions import DoesNotExist
from tortoise.query_utils import Prefetch
from ..core.cache import redis
from ..db.models import Users, Routes
from ..schemas import ResultResponse, default, menu
from ..utils.exceptions.user import (
    UserUnavailableException,
    PasswordValidateErrorException,
    UserNotExistException,
    TokenInvalidException,
)
from ..utils.log_util import log
from ..services import UserService

router = APIRouter()


@router.post(
    "/login",
    summary="登录",
    response_model=ResultResponse[default.Login],
)
async def login(
    request: Request,
    body: default.LoginIn,
):
    """用户登陆."""
    # 查询数据库有无此用户
    try:
        query_user = await UserService.query_user_by_username(username=body.username)
    except DoesNotExist:
        raise UserNotExistException
    # 用户为不可用状态
    if not query_user.status:
        raise UserUnavailableException
    # 验证密码
    if not md5_crypt.verify(secret=body.password, hash=query_user.password):
        raise PasswordValidateErrorException
    # 创建jwt
    access_token = create_access_token(data={"sub": query_user.user_name})
    return ResultResponse[default.Login](
        result=default.Login(
            data=query_user,
            access_token=access_token,
            token_type="bearer",
        )
    )


@router.post(
    "/logout",
    summary="退出登录",
    response_model=ResultResponse[None],
    # dependencies=[Depends(check_jwt_auth)],
)
async def logout(request: Request, current_user=Depends(current_user)):
    access_type, access_token = request.headers["authorization"].split(" ")
    # token加入黑名单列表
    await redis.aio_lpush(
        current_user.user_name + "-token-blacklist", access_token
    )
    return ResultResponse[None](message="Successfully logged out!")


@router.get(
    "/getRouters",
    summary="获取前端菜单路由",
    response_model=ResultResponse[List[menu.MenuTo]],
    dependencies=[Depends(check_jwt_auth)],
)
async def get_routers(current_user=Depends(current_user)):
    # 判断是否是admin角色用户, admin获取所有一级路由, 筛选status
    is_super = any(role.is_super for role in current_user.roles)
    if is_super:
        route_list = await Routes.filter(
            parent_id__isnull=True, status=1
        ).prefetch_related(
            Prefetch(
                "children",
                queryset=Routes.filter(status=1).prefetch_related(),
            ),
            "children__route_meta",
            "route_meta",
        )
    # 根据menus权限获取
    else:
        # 查询当前用户角色的路由权限
        user = (
            await Users.filter(id=current_user.id)
            .prefetch_related("roles__menus")
            .first()
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This user cannot access the routing menu!",
            )
        # 获取角色关联的所有菜单
        all_menus = {menu for role in user.roles for menu in role.menus}
        log.debug(all_menus)
        # 获取当前角色有权限的子路由的 ID 列表
        # 子路由
        sub_menus = [menu.id for menu in all_menus if menu.parent_id]
        # 父路由
        parent_menus = [menu.id for menu in all_menus if not menu.parent_id]
        log.debug(f"子路由：{sub_menus},父路由：{parent_menus}")
        # 使用Prefetch对预取进行复杂的查询，查询当前角色的子菜单
        route_list = await Routes.filter(
            id__in=parent_menus, status=1
        ).prefetch_related(
            # 使用Prefetch时，正常的prefetch_related操作也要查询
            Prefetch(
                "children",
                queryset=Routes.filter(id__in=sub_menus, status=1).prefetch_related(),
            ),
            "children__route_meta",
            "route_meta",
        )

    return ResultResponse[List[menu.MenuTo]](result=route_list)


@router.get(
    "/statistics",
    summary="统计数据",
    response_model=ResultResponse[str],
)
async def statistics_data():
    """统计测试数据"""
    pass