from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from .. import schemas
from src.db.models import Role, Users
from ..crud import UsersCrud
from ..utils.log_util import log


admin_api = APIRouter()


@admin_api.post(
    "/role/create",
    summary="创建角色",
    response_model=schemas.ResultResponse[schemas.RoleTo],
)
async def create_role(body: schemas.RoleIn):
    """创建角色

    Args:
        body (schemas.RoleIn): 请求体

    Returns:
        _type_: _description_
    """
    role_obj = await Role.create(**body.dict(exclude_unset=True))
    log.debug(f"role_name返回:{role_obj}")
    return schemas.ResultResponse[schemas.RoleTo](result=role_obj)


@admin_api.delete(
    "/role/{role_id}",
    summary="删除角色",
    response_model=schemas.ResultResponse[schemas.RoleTo],
)
async def delete_role(role_id: int):
    """删除角色

    Args:
        role_id (int): 角色id
    """
    pass


@admin_api.put(
    "/role/{role_id}",
    summary="更新角色",
    response_model=schemas.ResultResponse[schemas.RoleTo],
)
async def update_role(
    role_id: int,
):
    """修改角色

    Args:
        role_id (int): 角色id
    """
    pass


@admin_api.get(
    "/role/{role_id}",
    summary="查询角色",
    response_model=schemas.ResultResponse[schemas.RoleTo],
)
async def query_role(role_id):
    """查询某个角色

    Args:
        role_id (_type_): 角色id
    """
    return


@admin_api.get(
    "/role/roles",
    summary="查询所有角色",
    response_model=schemas.ResultResponse[schemas.RoleTo],
)
async def query_roles(
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
):
    """查询所有角色

    Args:
        limit (Optional[int], optional): 取值数. Defaults to 10.
        offset (Optional[int], optional): 偏移量. Defaults to 0.
    """
    pass


@admin_api.post(
    "/user/role",
    summary="新增用户角色",
    # response_model=schemas.ResultResponse[schemas.UserAddRoleTo],
)
async def add_user_role(res: schemas.UserAddRoleIn):
    user = await Users.filter(id=res.user_id).first().prefetch_related("roles")
    role = await Role.filter(name=res.role).first()
    if not role:
        return schemas.ResultResponse[str](message=f"role: {res.role} is not exist!")
    await user.roles.add(role)
    return schemas.ResultResponse[str]()


@admin_api.post("/premission", summary="新增角色权限")
async def set_role_premission():
    """设置角色权限"""
    pass


@admin_api.put("/premission/update", summary="修改角色权限")
async def update_role_premission():
    """修改角色权限"""
    pass


@admin_api.delete("/premission/delete", summary="删除角色权限")
async def delete_role_premission():
    """删除角色权限"""
    pass
