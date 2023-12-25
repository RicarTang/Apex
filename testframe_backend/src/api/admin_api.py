from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Response, status, Query
from tortoise.exceptions import DoesNotExist
from ..schemas import ResultResponse, user_schema, admin_schema
from ...src.db.models import Role, Users, Permission, AccessControl
from ..services import UserService, RolePermissionService
from ..utils.log_util import log
from ..core.authentication import Authority
from ..utils.exceptions.user import RoleNotExistException, UserNotExistException
from ..utils.exceptions.admin import (
    PermissionExistException,
    PermissionNotExistException,
    AccessNotExistException,
)


router = APIRouter()


@router.get(
    "/role/list",
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
    "/role",
    summary="新增角色",
    response_model=ResultResponse[user_schema.RoleTo],
    # dependencies=[Depends(Authority("admin,add"))],
)
async def add_role(body: user_schema.RoleIn):
    """创建角色

    Args:
        body (schemas.RoleIn): 请求体

    Returns:
        _type_: _description_
    """
    role_obj = await Role.create(**body.dict(exclude_unset=True))
    log.debug(f"role_name返回:{role_obj}")
    return ResultResponse[user_schema.RoleTo](result=role_obj)


@router.post(
    "/role/permission",
    summary="新增角色权限",
    response_model=ResultResponse[str],
)
async def add_role_permission(body: admin_schema.RolePermissionIn):
    """新增角色权限关联"""
    role = await Role.get_or_none(id=body.role_id)
    permission = await Permission.get_or_none(id=body.permission_id)
    if not role:
        raise RoleNotExistException
    if not permission:
        raise PermissionNotExistException
    await role.permissions.add(permission)
    return ResultResponse[str](message="successful!")


@router.delete(
    "/role/{role_id}",
    summary="删除角色",
    response_model=ResultResponse[str],
    dependencies=[Depends(Authority("admin","delete"))],
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


@router.put(
    "/role/{role_id}",
    summary="更新角色",
    response_model=ResultResponse[user_schema.RoleTo],
)
async def update_role(
    role_id: int,
):
    """修改角色

    Args:
        role_id (int): 角色id
    """
    pass


@router.post(
    "/user/role",
    summary="新增用户角色",
    response_model=ResultResponse[str],
)
async def add_user_role(body: user_schema.UserAddRoleIn):
    try:
        user = await Users.get(id=body.user_id).prefetch_related("roles")
    except DoesNotExist:
        raise UserNotExistException
    try:
        role = await Role.get(name=body.role_id)
    except DoesNotExist:
        raise RoleNotExistException
    await user.roles.add(role)
    return ResultResponse[str](message="User role association successful!")


@router.post(
    "/permission",
    summary="新增权限",
    response_model=ResultResponse[admin_schema.PermissionTo],
    # dependencies=[Depends(Authority("admin,add"))],
)
async def add_permission(body: admin_schema.PermissionIn):
    """新增权限"""
    get_permission = await Permission.get_or_none(name=body.name)
    if get_permission:
        raise PermissionExistException
    permission = await Permission.create(**body.dict(exclude_unset=True))
    return ResultResponse[admin_schema.PermissionTo](result=permission)


@router.post(
    "/access",
    summary="新增访问控制",
    response_model=ResultResponse[admin_schema.AccessTo],
)
async def add_access(body: admin_schema.AccessIn):
    """新增访问控制"""
    access = await AccessControl.create(**body.dict(exclude_unset=True))
    return ResultResponse[admin_schema.AccessTo](result=access)


@router.post(
    "/permission/access",
    summary="新增权限访问",
    response_model=ResultResponse[str],
)
async def add_permission_access(body: admin_schema.PermissionAccessIn):
    """新增权限访问控制"""
    permission = await Permission.get_or_none(id=body.permission_id)
    access = await AccessControl.get_or_none(id=body.access_id)
    if not permission:
        raise PermissionNotExistException
    if not access:
        raise AccessNotExistException
    await permission.accesses.add(access)
    return ResultResponse[str](message="success")


@router.put("/permission/{permission_id}", summary="修改权限")
async def update_role_permission(permission_id: int):
    """修改权限"""
    pass


@router.delete("/permission/{permission_id}", summary="删除权限")
async def delete_role_permission(permission_id: int):
    """删除权限"""
    pass
