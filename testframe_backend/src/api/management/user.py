from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path
from typing_extensions import Annotated
from pydantic import StringConstraints
from ...db.models import User
from ...schemas.management import user
from ...core.security import (
    # check_jwt_auth,
    get_current_user as current_user,
)

# from ...core.authentication import Authority
from ...schemas import ResultResponse
from ...services import UserService


router = APIRouter()


@router.get(
    "/list",
    summary="用户列表",
    response_model=ResultResponse[user.UsersTo],
)
async def get_users(
    username: Optional[str] = Query(
        default=None, description="用户名", alias="userName"
    ),
    status: Optional[str] = Query(default=None, description="用户状态"),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(
        default=None, description="结束时间", alias="endTime"
    ),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取用户列表"""

    result, total = await UserService.query_user_list(
        username, status, begin_time, end_time, limit, page
    )
    return ResultResponse[user.UsersTo](
        result=user.UsersTo(data=result, page=page, limit=limit, total=total)
    )


@router.get(
    "/me",
    summary="获取当前用户信息",
    response_model=ResultResponse[user.UserTo],
)
async def get_current_user(current_user: User = Depends(current_user)):
    """获取当前用户"""
    return ResultResponse[user.UserTo](result=current_user)


@router.post(
    "/add",
    summary="创建用户",
    response_model=ResultResponse[None],
    # dependencies=[Depends(Authority("user", "add"))],
)
async def create_user(body: user.UserIn):
    """创建用户."""
    result = await UserService.create_user(body)
    return ResultResponse[None](message="创建用户成功！")


@router.put(
    "/resetPwd",
    summary="重置用户密码",
    # dependencies=[Depends(Authority("user", "update"))],
)
async def reset_user_pwd(body: user.UserResetPwdIn):
    """更新用户密码"""
    await UserService.update_user_pwd(body.user_id, body.password)
    return ResultResponse[None](message="修改密码成功!")


@router.delete(
    "/{user_ids}",
    response_model=ResultResponse[None],
    summary="删除用户",
    # dependencies=[Depends(Authority("user", "delete"))],
)
async def delete_user(
    user_ids: Annotated[
        str,
        StringConstraints(strip_whitespace=True, pattern=r"^\d+(,\d+)*$"),
        Path(description="用户id字符串"),
    ]
):
    """删除用户."""
    await UserService.delete_user(user_ids)
    return ResultResponse[None](message="删除用户成功!")


@router.get(
    "/{user_id}",
    response_model=ResultResponse[user.UserTo],
    summary="根据id查询用户",
    # dependencies=[Depends(Authority("user", "query"))],
)
async def get_user(user_id: int):
    """根据id查询用户."""
    result = await UserService.query_user_by_id(user_id)
    return ResultResponse[user.UserTo](result=result)


# @router.put(
#     "/{user_id}",
#     response_model=ResultResponse[None],
#     summary="更新用户",
#     dependencies=[Depends(Authority("user", "update"))],
# )
# async def update_user(user_id: int, body: user.UserUpdateIn):
#     """更新用户信息."""
#     # 查询用户是否存在
#     query_user = await Users.filter(id=user_id).prefetch_related("roles").first()
#     if not query_user:
#         raise UserNotExistException
#     # 启用事务
#     async with in_transaction():
#         # 判断角色修改
#         if body.user_roles is not None:
#             if body.user_roles == []:
#                 raise HTTPException(
#                     status_code=status.HTTP_403_FORBIDDEN,
#                     detail="Role cannot be cleared!",
#                 )
#             # 获取当前用户角色列表
#             current_user_role_list = await query_user.roles.all()
#             # 获取接口请求角色列表
#             roles = await Role.filter(id__in=body.user_roles).all()
#             # 确定需要添加和需要移除的角色 ID
#             role_ids_to_add = list(set(roles) - set(current_user_role_list))
#             role_ids_to_remove = list(set(current_user_role_list) - set(roles))
#             log.debug(f"toadd:{role_ids_to_add},toremove:{role_ids_to_remove}")
#             # 添加/删除
#             await query_user.roles.add(*role_ids_to_add)
#             if role_ids_to_remove:
#                 await query_user.roles.remove(*role_ids_to_remove)
#         # 更新指定字段
#         await Users.filter(id=user_id).update(
#             **body.model_dump(exclude_unset=True, exclude=["user_roles"])
#         )
#     return ResultResponse[None](message=f"Update user information successfully!")
