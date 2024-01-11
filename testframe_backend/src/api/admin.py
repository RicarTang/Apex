from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query
from tortoise.transactions import in_transaction
from tortoise.query_utils import Prefetch
from ..schemas import ResultResponse, admin
from ..db.models import Role, Permission, Routes
from ..utils.log_util import log
from ..core.authentication import Authority
from ..utils.exceptions.user import RoleNotExistException
from ..utils.exceptions.admin import PermissionExistException


router = APIRouter()


@router.get(
    "/role/list",
    summary="角色列表",
    response_model=ResultResponse[admin.RolesTo],
)
async def query_roles(
    role_name: Optional[str] = Query(
        default=None, description="角色名称", alias="roleName"
    ),
    role_key: Optional[str] = Query(default=None, description="角色详情", alias="roleKey"),
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
        filters["role_name__icontains"] = role_name
    if role_key:
        filters["role_key__icontains"] = role_key
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
    query = Role.filter(**filters)
    result = (
        await query.prefetch_related(
            "permissions", "menus__children__route_meta", "menus__route_meta"
        )
        .offset(limit * (page - 1))
        .limit(limit)
        .all()
    )
    # total
    total = await query.count()
    return ResultResponse[admin.RolesTo](
        result=admin.RolesTo(data=result, page=page, limit=limit, total=total)
    )


@router.get(
    "/permission/list",
    summary="查询权限列表",
    response_model=ResultResponse[admin.PermissionsTo],
)
async def query_permissions(
    permission_name: Optional[str] = Query(
        default=None, description="权限名称", alias="permissionName"
    ),
    permission_model: Optional[str] = Query(
        default=None, description="权限模块", alias="permissionModel"
    ),
    permission_action: Optional[str] = Query(
        default=None, description="权限动作", alias="permissionAction"
    ),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """查询所有权限"""
    filters = {}
    if permission_name:
        filters["name__icontains"] = permission_name
    if permission_model:
        filters["model__icontains"] = permission_model
    if permission_action:
        filters["action__icontains"] = permission_action
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
    query = Permission.filter(**filters)
    permissions = await query.offset(limit * (page - 1)).limit(limit).all()
    total = await query.count()
    return ResultResponse[admin.PermissionsTo](
        result=admin.PermissionsTo(
            data=permissions, page=page, limit=limit, total=total
        )
    )


@router.post(
    "/role",
    summary="新增角色",
    response_model=ResultResponse[admin.RoleTo],
    # dependencies=[Depends(Authority("admin", "add"))],
)
async def add_role(body: admin.RoleIn):
    """创建角色

    Args:
        body (schemas.RoleIn): 请求体

    Returns:
        _type_: _description_
    """
    async with in_transaction():
        # 新增role
        role_obj = await Role.create(
            **body.model_dump(
                include=["role_name", "role_key", "remark"],
                exclude_unset=True,
                # by_alias=True,
            )
        )
        # 查询permissino
        if body.permission_ids:
            permission_list = await Permission.filter(id__in=body.permission_ids).all()
            if not permission_list:
                log.debug("无permission")
            # 新增role_permission
            await role_obj.permissions.add(*permission_list)
        # 查询route
        if body.menu_ids:
            menu_list = await Routes.filter(id__in=body.menu_ids).all()
            if not menu_list:
                log.debug("无menu")
            # 新增role_menu
            await role_obj.menus.add(*menu_list)
        query = (
            await Role.filter(id=role_obj.id)
            .prefetch_related("permissions", "menus")
            .first()
        )
        return ResultResponse[admin.RoleTo](result=query)


@router.post(
    "/permission",
    summary="新增权限",
    response_model=ResultResponse[admin.PermissionTo],
    # dependencies=[Depends(Authority("admin,add"))],
)
async def add_permission(body: admin.PermissionIn):
    """新增权限"""
    get_permission = await Permission.get_or_none(name=body.name)
    if get_permission:
        raise PermissionExistException
    permission = await Permission.create(**body.model_dump(exclude_unset=True))
    return ResultResponse[admin.PermissionTo](result=permission)


@router.put("/permission/{permission_id}", summary="修改权限")
async def update_role_permission(permission_id: int):
    """修改权限"""
    pass


@router.delete("/permission/{permission_id}", summary="删除权限")
async def delete_role_permission(permission_id: int):
    """删除权限"""
    pass


@router.delete(
    "/role/delete",
    summary="删除角色",
    response_model=ResultResponse[None],
    dependencies=[Depends(Authority("admin", "delete"))],
)
async def delete_role(body: admin.DeleteRoleIn):
    """删除角色"""
    deleted_count = await Role.filter(id__in=body.role_ids).delete()
    if not deleted_count:
        raise RoleNotExistException
    return ResultResponse[None](message=f"successful deleted role!")


@router.get(
    "/role/{role_id}",
    summary="获取角色",
    response_model=ResultResponse[admin.RoleTo],
)
async def get_role(
    role_id: int,
):
    """获取角色

    Args:
        role_id (int): 角色id
    """
    # role = await Role.filter(id=role_id).prefetch_related("permissions","menus__children__route_meta","menus__route_meta").first()
    role = (
        await Role.filter(id=role_id)
        .prefetch_related(
            "permissions",
            "menus__children__route_meta",
            "menus__route_meta",
            # 只查询子菜单
            Prefetch(
                "menus",
                queryset=Routes.filter(parent_id__isnull=False).prefetch_related(),
            ),
        )
        .first()
    )
    if not role:
        raise RoleNotExistException
    return ResultResponse[admin.RoleTo](result=role)


@router.put(
    "/role/{role_id}",
    summary="更新角色",
    response_model=ResultResponse[None],
)
async def update_role(role_id: int, body: admin.RoleIn):
    """修改角色"""
    role = await Role.get_or_none(id=role_id).prefetch_related("permissions", "menus")
    if not role:
        raise RoleNotExistException
    async with in_transaction():
        # 更新role
        await Role.filter(id=role_id).update(
            **body.model_dump(
                include=["role_name", "role_key", "remark"],
                exclude_unset=True,
                # by_alias=True,
            )
        )
        # 更新关联菜单
        if body.menu_ids:
            # 获取接口请求菜单列表
            menu_list = await Routes.filter(id__in=body.menu_ids).all()
            # 获取请求角色菜单列表
            current_role_menu_list = await role.menus.all()
            log.debug(current_role_menu_list)

            # 确定需要添加和需要移除的菜单 ID
            menu_ids_to_add = list(set(menu_list) - set(current_role_menu_list))
            menu_ids_to_remove = list(set(current_role_menu_list) - set(menu_list))
            log.debug(f"toadd:{menu_ids_to_add},toremove:{menu_ids_to_remove}")
            # 添加/删除
            await role.menus.add(*menu_ids_to_add)
            if menu_ids_to_remove:
                await role.menus.remove(*menu_ids_to_remove)
        # 刷新
        # await role.refresh_from_db()
        return ResultResponse[None](message="successful updated role!")
