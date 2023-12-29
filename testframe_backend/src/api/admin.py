from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Response, status, Query
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction
from ..schemas import ResultResponse, user_schema, admin_schema
from ..db.models import Role, Users, Permission, AccessControl, Routes, RouteMeta
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
    summary="角色列表",
    response_model=ResultResponse[admin_schema.RolesTo],
)
async def query_roles(
    role_name: Optional[str] = Query(
        default=None, description="角色名称", alias="roleName"
    ),
    role_key: Optional[str] = Query(
        default=None, description="角色详情", alias="roleKey"
    ),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取角色列表"""
    # 筛选列表
    filters = {}
    if role_name:
        filters["rolename__icontains"] = role_name
    if role_key:
        filters["rolekey__icontains"] = role_key
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
    query = Role.filter(**filters).prefetch_related("permissions__accesses")
    result = await query.offset(limit * (page - 1)).limit(limit).all()
    # total
    total = await query.count()
    return ResultResponse[admin_schema.RolesTo](
        result=admin_schema.RolesTo(data=result, page=page, limit=limit, total=total)
    )


@router.get(
    "/permission/list",
    summary="查询权限列表",
    response_model=ResultResponse[admin_schema.PermissionsTo],
)
async def query_permissions(
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """查询所有权限"""
    permissions = (
        await Permission.all()
        .prefetch_related("accesses")
        .offset(limit * (page - 1))
        .limit(limit)
    )
    total = await Permission.all().count()
    return ResultResponse[admin_schema.PermissionsTo](
        result=admin_schema.PermissionsTo(
            data=permissions, page=page, limit=limit, total=total
        )
    )


@router.post(
    "/role",
    summary="新增角色",
    response_model=ResultResponse[admin_schema.RoleTo],
    # dependencies=[Depends(Authority("admin,add"))],
)
async def add_role(body: admin_schema.RoleIn):
    """创建角色

    Args:
        body (schemas.RoleIn): 请求体

    Returns:
        _type_: _description_
    """
    role_obj = await Role.create(**body.dict(exclude_unset=True))
    log.debug(f"role_name返回:{role_obj}")
    return ResultResponse[admin_schema.RoleTo](result=role_obj)


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
    return ResultResponse[str](result="Successfully added role permissions!")


@router.post(
    "/user/role",
    summary="新增用户角色",
    response_model=ResultResponse[str],
)
async def add_user_role(body: admin_schema.UserAddRoleIn):
    try:
        user = await Users.get(id=body.user_id)
    except DoesNotExist:
        raise UserNotExistException
    try:
        role = await Role.get(name=body.role_id)
    except DoesNotExist:
        raise RoleNotExistException
    await user.roles.add(role)
    return ResultResponse[str](result="User role association successful!")


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
    return ResultResponse[str](result="Successfully added permission access")


@router.put("/permission/{permission_id}", summary="修改权限")
async def update_role_permission(permission_id: int):
    """修改权限"""
    pass


@router.delete("/permission/{permission_id}", summary="删除权限")
async def delete_role_permission(permission_id: int):
    """删除权限"""
    pass


@router.post(
    "/addMenu",
    summary="添加菜单",
    response_model=ResultResponse[admin_schema.AddMenuTo],
)
async def add_menu(body: admin_schema.AddMenuIn):
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
    return ResultResponse[admin_schema.AddMenuTo](result=result)


@router.put(
    "/role/{role_id}",
    summary="更新角色",
    response_model=ResultResponse[admin_schema.RoleTo],
)
async def update_role(
    role_id: int,
):
    """修改角色

    Args:
        role_id (int): 角色id
    """
    pass


@router.delete(
    "/role/{role_id}",
    summary="删除角色",
    response_model=ResultResponse[str],
    dependencies=[Depends(Authority("admin", "delete"))],
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
