from typing import Optional, Union
from datetime import datetime
from fastapi import APIRouter, Query, Request, Body, Depends
from tortoise.exceptions import DoesNotExist
from ..db.models import TestEnv
from ..services.testenv import TestEnvService
from ..schemas import ResultResponse, testenv
from ..utils.exceptions.testenv import TestEnvNotExistException
from ..utils.log_util import log


router = APIRouter()


@router.post(
    "/add",
    summary="添加测试环境地址",
    response_model=ResultResponse[testenv.TestEnvTo],
)
async def add_test_env(body: testenv.TestEnvIn):
    """添加测试环境地址

    Args:
        body (testenv.TestEnvIn): _description_
    """
    result = await TestEnv.create(**body.model_dump())
    return ResultResponse[testenv.TestEnvTo](result=result)


@router.get(
    "/list",
    summary="获取测试环境列表",
    response_model=ResultResponse[testenv.TestEnvsTo],
)
async def get_all_env(
    env_name: Optional[str] = Query(
        default=None, alias="envName", description="环境名称筛选"
    ),
    env_url: Optional[str] = Query(
        default=None, alias="envUrl", description="环境变量url筛选"
    ),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取环境变量列表"""
    filters = {}
    if env_name:
        filters["env_name__icontains"] = env_name
    if env_url:
        filters["env_url__icontains"] = env_url
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
    query = TestEnv.filter(**filters)
    test_env_list = await query.offset(limit * (page - 1)).limit(limit).all()
    total = await query.count()
    return ResultResponse[testenv.TestEnvsTo](
        result=testenv.TestEnvsTo(
            data=test_env_list,
            page=page,
            limit=limit,
            total=total,
        )
    )


@router.get(
    "/getCurrentEnv",
    summary="获取当前环境变量",
    response_model=ResultResponse[str],
)
async def get_current_env():
    """获取当前环境变量"""
    result = await TestEnvService().aio_get_current_env()
    return ResultResponse[str](result=result)


@router.post(
    "/setCurrentEnv",
    summary="设置当前环境变量",
)
async def set_current_env(
    body: testenv.CurrentEnvIn,
):
    """设置当前环境变量

    Args:
        env_id (int, optional): _description_. Defaults to Body().
    """
    await TestEnvService().aio_set_current_env("http://127.0.0.1:4000")
    return 1


@router.get(
    "/{env_id}",
    summary="获取指定环境变量",
    response_model=ResultResponse[testenv.TestEnvTo],
)
async def get_env(env_id: int):
    """获取指定环境

    Args:
        env_id (int): 环境id
    """
    try:
        result = await TestEnv.get(id=env_id)
    except DoesNotExist:
        raise TestEnvNotExistException
    return ResultResponse[testenv.TestEnvTo](result=result)


@router.put(
    "/{env_id}",
    summary="更新env info",
    response_model=ResultResponse[str],
)
async def update_env(
    env_id: int,
    body: testenv.TestEnvIn,
):
    """更新env数据信息"""
    if not await TestEnv.filter(id=env_id).exists():
        raise TestEnvNotExistException
    await TestEnv.filter(id=env_id).update(**body.model_dump(exclude_unset=True))
    return ResultResponse[str](result="successful update environment!")


@router.delete(
    "",
    summary="删除环境变量",
    response_model=ResultResponse[str],
)
async def delete_env(body: testenv.DeleteEnvIn):
    """删除指定环境"""
    if not await TestEnv.filter(id__in=body.env_ids).exists():
        raise TestEnvNotExistException
    await TestEnv.filter(id__in=body.env_ids).delete()
    return ResultResponse[str](result="successful deleted environment!")
