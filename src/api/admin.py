from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from .. import schemas
from src.db.models import Role, Users
from ..crud import UsersCrud, RolePermCrud
from ..utils.log_util import log
from ..core.authentication import get_casbin, Authority


router = APIRouter()


@router.post(
    "/role/create",
    summary="创建角色",
    response_model=schemas.ResultResponse[schemas.RoleTo],
    dependencies=[Depends(Authority("admin,add"))]
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


@router.delete(
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


@router.put(
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


@router.get(
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


@router.get(
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


@router.post(
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


@router.post(
    "/permission",
    summary="新增角色权限",
    response_model=schemas.ResultResponse[str],
    dependencies=[Depends(Authority("admin,add"))],
)
async def set_role_permission(req: schemas.RolePermIn):
    """设置角色权限"""
    # 查询角色
    role = await RolePermCrud.query_role(name=req.role)
    if not role:
        return schemas.ResultResponse[str](
            code=404, message=f"Role:{req.role} does not exist!"
        )
    e = await get_casbin()
    if await e.add_permission_for_role(req.role, req.model, req.act):
        return schemas.ResultResponse[str]()
    return schemas.ResultResponse[str](
        message="Description Failed to add the role permission because the role permission already exists!"
    )


@router.put("/permission/update", summary="修改角色权限")
async def update_role_permission():
    """修改角色权限"""
    pass


@router.delete("/permission/delete", summary="删除角色权限")
async def delete_role_permission():
    """删除角色权限"""
    pass
