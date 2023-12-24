import json
from typing import List
from fastapi import APIRouter, Depends, Request
from ..core.security import (
    create_access_token,
    check_jwt_auth,
)
from passlib.hash import md5_crypt
from tortoise.exceptions import DoesNotExist
from ...src.db.models import Users, Routes
from ..schemas import ResultResponse, user_schema, default_schema
from ..utils.exceptions.user import (
    UserUnavailableException,
    PasswordValidateErrorException,
    UserNotExistException,
    TokenInvalidException,
)
from ..utils.log_util import log
from ..services import UserTokenService
from ..core.security import (
    check_jwt_auth,
    get_current_user as current_user,
)

router = APIRouter()


@router.post(
    "/login",
    summary="登录",
    response_model=ResultResponse[user_schema.Login],
)
async def login(
    request: Request,
    user: user_schema.LoginIn,
):
    """用户登陆."""
    # 查询数据库有无此用户
    try:
        query_user = await Users.get(username=user.username)
    except DoesNotExist:
        raise UserNotExistException
    # 用户为不可用状态
    if not query_user.is_active:
        raise UserUnavailableException
    # 验证密码
    if not md5_crypt.verify(secret=user.password, hash=query_user.password):
        raise PasswordValidateErrorException
    # 创建jwt
    access_token = create_access_token(data={"sub": query_user.username})
    # 更新用户jwt
    await UserTokenService.add_jwt(
        current_user_id=query_user.id, token=access_token, client_ip=request.client.host
    )
    return ResultResponse[user_schema.Login](
        result=user_schema.Login(
            data=query_user,
            access_token=access_token,
            token_type="bearer",
        )
    )


@router.post(
    "/logout",
    summary="退出登录",
    response_model=ResultResponse[str],
    dependencies=[Depends(check_jwt_auth)],
)
async def logout(request: Request):
    # 修改当前用户数据库token状态为0
    access_type, access_token = request.headers["authorization"].split(" ")
    if not await UserTokenService.update_token_state(token=access_token):
        raise TokenInvalidException
    return ResultResponse[str](result="Successfully logged out!")


@router.get(
    "/getRouters",
    summary="获取前端菜单路由",
    response_model=ResultResponse[List[default_schema.RoutesTo]],
    dependencies=[Depends(check_jwt_auth)],
)
async def get_routers(current_user=Depends(current_user)):
    # 控制路由权限
    if current_user.id in [1, 2]:
        # 仅查询一级路由,并预取children(children里的meta)与meta
        route_list = await Routes.filter(parent_id__isnull=True).prefetch_related(
            "children__meta", "meta"
        )
    else:
        route_list = await Routes.filter(
            parent_id__isnull=True, is_admin_visible__not=True
        ).prefetch_related("children__meta", "meta")
    return ResultResponse[List[default_schema.RoutesTo]](result=route_list)
