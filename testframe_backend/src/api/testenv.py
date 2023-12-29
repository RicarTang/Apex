from typing import Optional
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
async def add_test_env_ip(body: testenv.TestEnvIn):
    """添加测试环境地址

    Args:
        body (testenv.TestEnvIn): _description_
    """
    result = await TestEnv.create(**body.dict())
    return ResultResponse[testenv.TestEnvTo](result=result)


@router.get(
    "/getAll",
    summary="获取所有环境url",
    response_model=ResultResponse[testenv.TestEnvsTo],
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
    summary="获取指定环境url",
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
    response_model=ResultResponse[testenv.TestEnvTo],
)
async def update_env(
    env_id: int,
    body: testenv.TestEnvIn,
):
    """更新env数据信息

    Args:
        env_id (int): _description_
        body (testenv.TestEnvIn): _description_

    Returns:
        _type_: _description_
    """
    if not await TestEnv.filter(id=env_id).exists():
        raise TestEnvNotExistException
    result = await TestEnv.filter(id=env_id).update(**body.dict(exclude_unset=True))
    log.debug(f"update更新{result}条数据")
    return ResultResponse[testenv.TestEnvTo](result=await TestEnv.get(id=env_id))


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
