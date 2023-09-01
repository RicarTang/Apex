from typing import Optional
from fastapi import (
    APIRouter,
    Query,
)
from tortoise.exceptions import DoesNotExist
from ..db.models import TestSuite
from ..schemas import ResultResponse, testsuite_schema
from ..utils.log_util import log


router = APIRouter()


@router.post(
    "/add",
    summary="添加测试套件",
    response_model=ResultResponse[testsuite_schema.TestSuiteTo],
)
async def add_testsuite(body: testsuite_schema.TestSuiteIn):
    """新增测试套件

    Args:
        body (testsuite_schema.TestSuiteIn): _description_
    """
    result = await TestSuite.create(**body.dict())
    return ResultResponse[testsuite_schema.TestSuiteTo](result=result)


@router.get(
    "/getAll",
    summary="获取所有测试套件",
    response_model=ResultResponse[testsuite_schema.TestSuitesTo],
)
async def get_all_testsuite(
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取所有测试套件

    Args:
        limit (Optional[int], optional): _description_. Defaults to Query(default=20, ge=10).
        page (Optional[int], optional): _description_. Defaults to Query(default=1, gt=0).
    """
    testsuite_list = await TestSuite.all().offset(limit * (page - 1)).limit(limit)
    total = await TestSuite.all().count()
    return ResultResponse[testsuite_schema.TestSuitesTo](
        result=testsuite_schema.TestSuitesTo(
            data=testsuite_list,
            page=page,
            limit=limit,
            total=total,
        )
    )


@router.get(
    "/{suite_id}",
    summary="获取指定testsuite",
    response_model=ResultResponse[testsuite_schema.TestSuiteTo],
)
async def get_testsuite(suite_id: int):
    """获取指定测试套件

    Args:
        suite_id (int): _description_
    """
    try:
        result = await TestSuite.get(id=suite_id)
    except DoesNotExist:
        raise
    return ResultResponse[testsuite_schema.TestSuiteTo](result=result)


@router.put(
    "/{suite_id}",
    summary="更新测试套件",
    response_model=ResultResponse[testsuite_schema.TestSuiteTo],
)
async def update_testsuite(suite_id: int, body: testsuite_schema.TestSuiteIn):
    """更新测试套件数据

    Args:
        suite_id (int): _description_
        body (testsuite_schema.TestSuiteIn): _description_
    """
    if not await TestSuite.filter(id=suite_id).exists():
        raise
    result = await TestSuite.filter(id=suite_id).update(**body.dict(exclude_unset=True))
    log.debug(f"update更新{result}条数据")
    return ResultResponse[testsuite_schema.TestSuiteTo](
        result=await TestSuite.get(id=suite_id)
    )


@router.delete(
    "/{suite_id}",
    summary="删除测试套件",
    response_model=ResultResponse[str],
)
async def delete_testsuite(suite_id: int):
    """删除指定id测试套件

    Args:
        suite_id (int): _description_
    """
    if not await TestSuite.filter(id=suite_id).exists():
        raise
    result = await TestSuite.filter(id=suite_id).delete()
    return ResultResponse[str](message="successful deleted testsuite!")
