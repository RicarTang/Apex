from fastapi import APIRouter, HTTPException, Depends
from .. import schemas
from src.db.models import Role
from ..utils.log_util import log


admin_api = APIRouter()


@admin_api.post("/create", summary="创建角色", response_model=schemas.RoleTo)
async def create_role(name: schemas.RoleIn):
    """创建角色api

    Args:
        name (schemas.RoleIn): name角色名称

    Returns:
        _type_: _description_
    """
    role_obj = await Role.create(**name.dict(exclude_unset=True))
    log.debug(f"role_name返回:{role_obj}")
    return schemas.RoleTo(data=role_obj)
