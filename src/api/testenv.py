from typing import Optional
from fastapi import APIRouter, Query, Request, Body, Depends
from tortoise.exceptions import DoesNotExist
from aioredis import Redis
from ..core.cache import aioredis_pool
from ..core.test.api_test import ApiTestDependency
from ..db.models import TestEnv
from ..schemas import ResultResponse, testenv_schema
from ..utils.exceptions.testenv import TestEnvNotExistException
from ..utils.log_util import log



router = APIRouter()


@router.post(
    "/add",
    summary="添加测试环境地址",
    response_model=ResultResponse[testenv_schema.TestEnvTo],
)
async def add_test_env_ip(body: testenv_schema.TestEnvIn):
    """添加测试环境地址

    Args:
        body (testenv_schema.TestEnvIn): _description_
    """
    result = await TestEnv.create(**body.dict())
    return ResultResponse[testenv_schema.TestEnvTo](result=result)


@router.get(
    "/getAll",
    summary="获取所有环境url",
    response_model=ResultResponse[testenv_schema.TestEnvsTo],
)
async def get_all_env(
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取所有环境url

    Args:
        limit (Optional[int], optional): _description_. Defaults to Query(default=20, ge=10).
        page (Optional[int], optional): _description_. Defaults to Query(default=1, gt=0).
    """
    test_env_list = await TestEnv.all().offset(limit * (page - 1)).limit(limit)
    total = await TestEnv.all().count()
    return ResultResponse[testenv_schema.TestEnvsTo](
        result=testenv_schema.TestEnvsTo(
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
async def get_current_env(api_test: ApiTestDependency = Depends()):
    """获取当前环境变量

    Args:
        redis (Redis, optional): _description_. Defaults to Depends(aioredis_pool).
    """
    result = await api_test.get_current_env()
    return ResultResponse[str](result=result)


@router.get(
    "/{env_id}",
    summary="获取指定环境url",
    response_model=ResultResponse[testenv_schema.TestEnvTo],
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
    return ResultResponse[testenv_schema.TestEnvTo](result=result)


@router.put(
    "/{env_id}",
    summary="更新env info",
    response_model=ResultResponse[testenv_schema.TestEnvTo],
)
async def update_env(
    env_id: int,
    body: testenv_schema.TestEnvIn,
):
    """更新env数据信息

    Args:
        env_id (int): _description_
        body (testenv_schema.TestEnvIn): _description_

    Returns:
        _type_: _description_
    """
    if not await TestEnv.filter(id=env_id).exists():
        raise TestEnvNotExistException
    result = await TestEnv.filter(id=env_id).update(**body.dict(exclude_unset=True))
    log.debug(f"update更新{result}条数据")
    return ResultResponse[testenv_schema.TestEnvTo](result=await TestEnv.get(id=env_id))


@router.delete(
    "/{env_id}",
    summary="删除指定环境",
    response_model=ResultResponse[str],
)
async def delete_env(env_id: int):
    """删除指定环境

    Args:
        env_id (int): _description_
    """
    if not await TestEnv.filter(id=env_id).exists():
        raise TestEnvNotExistException
    result = await TestEnv.filter(id=env_id).delete()
    return ResultResponse[str](message="successful deleted environment!")


@router.post(
    "/setCurrentEnv",
    summary="设置当前环境变量",
)
async def set_current_env(
    env_id: int = Body(...), api_test: ApiTestDependency = Depends()
):
    """设置当前环境变量

    Args:
        env_id (int, optional): _description_. Defaults to Body().
    """
    await api_test.set_current_env("currentEnv", "http://127.0.0.1")
    return 1
