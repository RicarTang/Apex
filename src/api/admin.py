from fastapi import APIRouter, HTTPException, Depends
from .. import schemas
from src.db.models import Role, Permission
from ..utils.log_util import log


admin_api = APIRouter()


@admin_api.post("/role/create", summary="创建角色", response_model=schemas.RoleTo)
async def create_role(body: schemas.RoleIn):
    """创建角色api

    Args:
        body (schemas.RoleIn): 请求体

    Returns:
        _type_: _description_
    """
    role_obj = await Role.create(**body.dict(exclude_unset=True))
    log.debug(f"role_name返回:{role_obj}")
    return schemas.RoleTo(data=role_obj)


@admin_api.post(
    "/permission/create", summary="创建权限", response_model=schemas.PermissionTo
)
async def creaet_permission(body: schemas.PermissionIn):
    """新增权限"""
    permission_obj = await Permission.create(**body.dict(exclude_unset=True))
    log.debug(f"permission_obj返回：{permission_obj}")
    return schemas.PermissionTo(data=permission_obj)

@admin_api.delete("/permission/{permission_id}", summary="删除权限")
async def delete_permission():
    """删除单个权限"""
    pass