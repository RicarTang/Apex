from fastapi import APIRouter, HTTPException, Depends
from .. import schemas
from src.db.models import Role
from ..utils.log_util import log


admin_api = APIRouter()


@admin_api.post("/role/create", summary="创建角色", response_model=schemas.ResultResponse[schemas.RoleTo])
async def create_role(body: schemas.RoleIn):
    """创建角色api

    Args:
        body (schemas.RoleIn): 请求体

    Returns:
        _type_: _description_
    """
    role_obj = await Role.create(**body.dict(exclude_unset=True))
    log.debug(f"role_name返回:{role_obj}")
    return schemas.ResultResponse[schemas.RoleTo](result=role_obj)



