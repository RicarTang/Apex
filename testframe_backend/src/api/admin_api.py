from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Response, status, Query
from tortoise.exceptions import DoesNotExist
from ..schemas import ResultResponse, user_schema
from ...src.db.models import Role, Users
from ..services import UserService, RolePermissionService
from ..utils.log_util import log
from ..core.authentication import get_casbin, Authority
from ..utils.exceptions.user import RoleNotExistException, UserNotExistException


router = APIRouter()


@router.get(
    "/role/roles",
    summary="查询所有角色",
    response_model=ResultResponse[user_schema.RolesTo],
)
async def query_roles(
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """查询所有角色

    Args:
        limit (Optional[int], optional): 取值数. Defaults to 10.
        page (Optional[int], optional): 页数. Defaults to 0.
    """
    roles = await Role.all().offset(limit * (page - 1)).limit(limit)
    total = await Role.all().count()
    return ResultResponse[user_schema.RolesTo](
        result=user_schema.RolesTo(data=roles, page=page, limit=limit, total=total)
    )


@router.post(
    "/role/create",
    summary="创建角色",
    response_model=ResultResponse[user_schema.RoleTo],
    dependencies=[Depends(Authority("admin,add"))],
)
async def create_role(body: user_schema.RoleIn):
    """创建角色

    Args:
        body (schemas.RoleIn): 请求体

    Returns:
        _type_: _description_
    """
    role_obj = await Role.create(**body.dict(exclude_unset=True))
    log.debug(f"role_name返回:{role_obj}")
    return ResultResponse[user_schema.RoleTo](result=role_obj)


@router.delete(
    "/role/{role_id}",
    summary="删除角色",
    response_model=ResultResponse[str],
    dependencies=[Depends(Authority("admin,delete"))],
)
async def delete_role(role_id: int):
    """删除角色

    Args:
        role_id (int): 角色id
    """
    deleted_count = await Role.filter(id=role_id).delete()
    log.debug(f"删除角色id：{deleted_count}")
    if not deleted_count:
        raise RoleNotExistException
    return ResultResponse[str](message=f"successful deleted role!")


# @router.put(
#     "/role/{role_id}",
#     summary="更新角色",
#     response_model=schemas.ResultResponse[schemas.RoleTo],
# )
# async def update_role(
#     role_id: int,
# ):
#     """修改角色

#     Args:
#         role_id (int): 角色id
#     """
#     pass


@router.get(
    "/role/{role_id}",
    summary="查询角色",
    response_model=ResultResponse[user_schema.RoleTo],
)
async def query_role(
    role_id: int,
):
    """查询某个角色

    Args:
        role_id (_type_): 角色id
    """
    try:
        role = await Role.get(id=role_id)
    except DoesNotExist:
        raise RoleNotExistException
    return ResultResponse[user_schema.RoleTo](result=role)


@router.post(
    "/user/role",
    summary="新增用户角色",
    response_model=ResultResponse[None],
)
async def add_user_role(req: user_schema.UserAddRoleIn):
    try:
        user = await Users.get(id=req.user_id).prefetch_related("roles")
    except DoesNotExist:
        raise UserNotExistException
    try:
        role = await Role.get(name=req.role)
    except DoesNotExist:
        raise RoleNotExistException
    await user.roles.add(role)
    return ResultResponse[str]()


@router.post(
    "/permission",
    summary="新增角色权限",
    response_model=ResultResponse[str],
    dependencies=[Depends(Authority("admin,add"))],
)
async def set_role_permission(req: user_schema.RolePermIn):
    """设置角色权限"""
    # 查询角色
    role = await RolePermissionService.query_role(name=req.role)
    if not role:
        raise RoleNotExistException
    e = await get_casbin()
    if await e.add_permission_for_role(req.role, req.model, req.act):
        return ResultResponse[str]()
    return ResultResponse[str](
        message="Description Failed to add the role permission because the role permission already exists!"
    )


# @router.put("/permission/update", summary="修改角色权限")
# async def update_role_permission():
#     """修改角色权限"""
#     pass


# @router.delete("/permission/delete", summary="删除角色权限")
# async def delete_role_permission():
#     """删除角色权限"""
#     pass
