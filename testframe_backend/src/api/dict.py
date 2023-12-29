from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from ..core.security import (
    create_access_token,
    check_jwt_auth,
)
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from ..db.models import Users, Routes, DataDict
from ..schemas import ResultResponse, system_schema
from ..utils.exceptions.user import (
    UserUnavailableException,
    PasswordValidateErrorException,
    UserNotExistException,
    TokenInvalidException,
)
from ..utils.log_util import log
from ..services import SystemService
from ..core.security import (
    check_jwt_auth,
    get_current_user as current_user,
)

router = APIRouter()


@router.get(
    "/dataDict",
    summary="获取数据字典",
    response_model=ResultResponse[List[system_schema.DataDictTo]],
)
async def get_data_dict(dict_type: str = Query(alias="dictType")):
    """获取指定类型数据字典"""
    result = await SystemService.query_dict_by_type(dict_type)
    return ResultResponse[List[system_schema.DataDictTo]](result=result)


@router.post(
    "/dataDict",
    summary="设置数据字典",
    response_model=ResultResponse[system_schema.DataDictTo],
)
async def set_data_dict(body: system_schema.DataDictIn):
    """新增数据字典"""
    result = await SystemService.add_data_dict(body)
    return ResultResponse[system_schema.DataDictTo](result=result)
