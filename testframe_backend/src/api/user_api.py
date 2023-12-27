from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Response
from passlib.hash import md5_crypt
from tortoise.transactions import in_transaction
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist
from ..core.security import (
    check_jwt_auth,
    get_current_user as current_user,
)
from ..core.authentication import Authority
from ...src.db.models import Users, Role
from ..schemas import ResultResponse, user_schema, admin_schema
from ..utils.log_util import log
from ..utils.exceptions.user import (
    UserNotExistException,
    RoleNotExistException,
)
from ..services import UserService


router = APIRouter()


@router.get(
    "/list",
    summary="获取所有用户",
    response_model=ResultResponse[user_schema.UsersTo],
)
async def get_users(
    username: Optional[str] = Query(default=None, description="用户名", alias="userName"),
    is_active: Optional[str] = Query(default=None, description="用户状态"),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取用户列表"""
    # 筛选列表
    filters = {}
    if username:
        filters["username__icontains"] = username
    if is_active is not None:
        filters["is_active"] = is_active
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
    # 执行查询
    query = (
        Users.filter(**filters)
        .prefetch_related("roles")
        .offset(limit * (page - 1))
        .limit(limit)
    )
    result = await query.all()
    # total
    total = await query.count()
    return ResultResponse[user_schema.UsersTo](
        result=user_schema.UsersTo(data=result, page=page, limit=limit, total=total)
    )


@router.get(
    "/role",
    summary="获取当前用户角色",
    response_model=ResultResponse[List[admin_schema.RoleTo]],
)
async def query_user_role(
    current_user: Users = Depends(current_user),
):
    """查询当前用户角色"""
    user = (
        await Users.filter(id=current_user.id)
        .first()
        .prefetch_related("roles__permissions__accesses")
    )
    return ResultResponse[List[admin_schema.RoleTo]](result=user.roles)


@router.get(
    "/me",
    summary="获取当前用户信息",
    response_model=ResultResponse[user_schema.UserTo],
)
async def get_current_user(current_user: Users = Depends(current_user)):
    """获取当前用户"""
    return ResultResponse[user_schema.UserTo](result=current_user)


@router.post(
    "/create",
    summary="创建用户",
    response_model=ResultResponse[user_schema.UserTo],
    dependencies=[Depends(Authority("user", "add"))],
)
async def create_user(body: user_schema.UserIn):
    """创建用户."""
    async with in_transaction():
        body.password = md5_crypt.hash(body.password)
        user_obj = await Users.create(**body.model_dump(exclude_unset=True))
        # 查询角色列表
        roles = await Role.filter(id__in=body.user_roles).all()
        log.debug(roles)
        if not roles:
            raise RoleNotExistException
        # 添加角色关联
        await user_obj.roles.add(*roles)
    log.info(f"成功创建用户：{body.model_dump(exclude_unset=True)}")
    return ResultResponse[user_schema.UserTo](
        result=await UserService.query_user_by_id(user_obj.id)
    )


@router.delete(
    "/batchDelete",
    summary="批量删除用户",
    response_model=ResultResponse[str],
    dependencies=[Depends(Authority("user", "delete"))],
)
async def batch_delete_user(body: user_schema.BatchDelete):
    """批量删除用户

    Args:
        body (user_schema.BatchDelete): _description_

    Returns:
        _type_: _description_
    """
    async with in_transaction():  # 事务
        # 使用 filter 方法过滤出要删除的记录，然后delete删除
        users_to_delete = await Users.filter(id__in=body.users_id).delete()
    return ResultResponse[str](message=f"successful deleted {users_to_delete} users!")


@router.get(
    "/{user_id}",
    response_model=ResultResponse[user_schema.UserTo],
    summary="根据id查询用户",
    dependencies=[Depends(Authority("user", "query"))],
)
async def get_user(user_id: int):
    """根据id查询用户."""
    try:
        user = await Users.get(id=user_id)
    except DoesNotExist:
        raise UserNotExistException
    return ResultResponse[user_schema.UserTo](result=user)


@router.put(
    "/{user_id}",
    response_model=ResultResponse[user_schema.UserTo],
    summary="更新用户",
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(Authority("user", "update"))],
)
async def update_user(user_id: int, user: user_schema.UserIn):
    """更新用户信息."""
    # 使用 atomic 事务
    async with in_transaction():
        # 查询用户是否存在
        existing_user = await Users.get_or_none(id=user_id)
        if not existing_user:
            raise UserNotExistException
        # 如果提供了密码，进行密码哈希
        if user.password:
            user.password = md5_crypt.hash(user.password)

        # 使用 filter 更新指定字段
        result = await Users.filter(id=user_id).update(**user.dict(exclude_unset=True))
        log.debug(f"update 更新{result}条数据")

        # 获取更新后的用户信息
        updated_user = await Users.get(id=user_id)
        return ResultResponse[user_schema.UserTo](result=updated_user)


@router.delete(
    "/{user_id}",
    response_model=ResultResponse[str],
    summary="删除用户",
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(Authority("user", "delete"))],
)
async def delete_user(user_id: int, response: Response):
    """删除用户."""
    if not await Users.filter(id=user_id).exists():
        raise UserNotExistException
    deleted_count = await Users.filter(id=user_id).delete()
    return ResultResponse[str](message="successful deleted user!")
