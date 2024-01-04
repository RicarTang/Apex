from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Query
from ..db.models import Users, Routes, DataDict
from ..schemas import ResultResponse, data_dict
from ..utils.log_util import log
from ..services import DataDictService
from ..core.security import (
    check_jwt_auth,
    get_current_user as current_user,
)

router = APIRouter()


@router.get(
    "/list",
    summary="数据字典列表",
    response_model=ResultResponse[data_dict.DataDictsTo],
)
async def get_dict_list(
    dict_type: Optional[str] = Query(
        default=None, alias="dictType", description="字典类型筛选"
    ),
    dict_label: Optional[str] = Query(
        default=None, alias="dictName", description="字典label筛选"
    ),
    is_default: Optional[str] = Query(
        default=None, alias="isDefault", description="字典值是否默认筛选"
    ),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取数据字典列表"""
    filters = {}
    if dict_type:
        filters["dict_type__icontains"] = dict_type
    if dict_label:
        filters["dict_label__icontains"] = dict_label
    if is_default:
        filters["is_default__icontains"] = is_default
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
    query = DataDict.filter(**filters)
    data_dict_list = await query.offset(limit * (page - 1)).limit(limit).all()
    total = await query.count()
    return ResultResponse[data_dict.DataDictsTo](
        result=data_dict.DataDictsTo(
            data=data_dict_list,
            page=page,
            limit=limit,
            total=total,
        )
    )


@router.get(
    "/dataDict",
    summary="获取数据字典",
    response_model=ResultResponse[List[data_dict.DataDictTo]],
)
async def get_data_dict(dict_type: str = Query(alias="dictType")):
    """获取指定类型数据字典"""
    result = await DataDictService.query_dict_by_type(dict_type)
    return ResultResponse[List[data_dict.DataDictTo]](result=result)


@router.post(
    "/dataDict",
    summary="设置数据字典",
    response_model=ResultResponse[data_dict.DataDictTo],
)
async def set_data_dict(body: data_dict.DataDictIn):
    """新增数据字典"""
    result = await DataDictService.add_data_dict(body)
    return ResultResponse[data_dict.DataDictTo](result=result)
