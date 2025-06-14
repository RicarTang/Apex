"""用户访问控制"""

from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Query
from pydantic import StringConstraints
from ...schemas.management.user import (
    UserListOut,
    UserOut,
    UserIn,
    UserResetPwdIn,
    UserUpdateIn,
)
from ...core.security import (
    # check_jwt_auth,
    get_current_user as current_user,
)
from ...core.authentication import Authority
from ...db.models import Users
from ...schemas import ResultResponse
from ...utils.log_util import log
from ...services import UserService


router = APIRouter()


@router.get(
    "/list",
    summary="用户列表",
    response_model=ResultResponse[UserListOut],
)
async def get_users(
    username: Optional[str] = Query(
        default=None,
        description="用户名",
        alias="userName",
    ),
    user_status: Optional[str] = Query(
        default=None, description="用户状态", alias="status"
    ),
    begin_time: Optional[str] = Query(
        default=None,
        description="开始时间",
        alias="beginTime",
    ),
    end_time: Optional[str] = Query(
        default=None,
        description="结束时间",
        alias="endTime",
    ),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取用户列表"""
    result, total = await UserService.query_user_list(
        username=username,
        user_status=user_status,
        begin_time=begin_time,
        end_time=end_time,
        limit=limit,
        page=page,
    )
    return ResultResponse[UserListOut](
        result=UserListOut(data=result, page=page, limit=limit, total=total)
    )


@router.get(
    "/me",
    summary="获取当前用户信息",
    response_model=ResultResponse[UserOut],
)
async def get_current_user(cur_user: Users = Depends(current_user)):
    """获取当前用户"""
    return ResultResponse[UserOut](result=cur_user)


@router.post(
    "/add",
    summary="创建用户",
    response_model=ResultResponse[UserOut],
    dependencies=[Depends(Authority("user", "add"))],
)
async def create_user(body: UserIn):
    """创建用户."""
    created_user = await UserService.create_user(body=body)
    return ResultResponse[UserOut](result=created_user)


@router.put(
    "/resetPwd",
    summary="重置用户密码",
    dependencies=[Depends(Authority("user", "update"))],
)
async def reset_user_pwd(body: UserResetPwdIn):
    """更新用户密码"""
    await UserService.update_user_pwd(body)
    return ResultResponse[None](message="successful reset user password!")


@router.delete(
    "/{user_ids}",
    response_model=ResultResponse[None],
    summary="删除用户",
    dependencies=[Depends(Authority("user", "delete"))],
)
async def delete_user(
    user_ids: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=r"^\d+(,\d+)*$")
    ]
):
    """删除用户."""
    log.debug(user_ids)
    # 解析User ids 为列表
    source_ids_list = user_ids.split(",")
    # 删除
    await UserService.delete_user_from_id(source_ids_list)
    return ResultResponse[None](message="successful deleted user!")


@router.get(
    "/{user_id}",
    response_model=ResultResponse[UserOut],
    summary="根据id查询用户",
    dependencies=[Depends(Authority("user", "query"))],
)
async def get_user(user_id: int):
    """根据id查询用户."""
    q_user = await UserService.query_user_by_id(user_id)
    return ResultResponse[UserOut](result=q_user)


@router.put(
    "/{user_id}",
    response_model=ResultResponse[None],
    summary="更新用户",
    dependencies=[Depends(Authority("user", "update"))],
)
async def update_user(user_id: int, body: UserUpdateIn):
    """更新用户信息."""
    await UserService.update_user_from_id(user_id=user_id, body=body)
    return ResultResponse[None](message="Update user information successfully!")
