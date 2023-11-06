from typing import Optional
from fastapi import (
    APIRouter,
    Query,
)
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction
from ..db.models import TestSuite, TestCase
from ..schemas import ResultResponse, testsuite_schema
from ..utils.log_util import log
from ..utils.exceptions.testsuite import TestsuiteNotExistException


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
    async with in_transaction():
        testsuite = await TestSuite.create(**body.dict())
        testcase_result = await TestCase.get(id=body.testcase_id)
        await testsuite.testcases.add(testcase_result)
        await testsuite.fetch_related('testcases')
    return ResultResponse[testsuite_schema.TestSuiteTo](result=testsuite)


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
    # 使用prefetch_related预取关联的testcase列表
    query_list = (
        await TestSuite.all()
        .prefetch_related("testcases")
        .offset(limit * (page - 1))
        .limit(limit)
    )
    # 使用pydantic的from_orm方法对关联的预取数据进行序列化
    testsuites_list = [
        testsuite_schema.TestSuiteTo.from_orm(testsuite) for testsuite in query_list
    ]
    total = await TestSuite.all().count()
    # return testsuites_list
    return ResultResponse[testsuite_schema.TestSuitesTo](
        result=testsuite_schema.TestSuitesTo(
            data=testsuites_list,
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
        result = await TestSuite.get(id=suite_id).prefetch_related("testcase")
    except DoesNotExist:
        raise TestsuiteNotExistException
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
        raise TestsuiteNotExistException
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
        raise TestsuiteNotExistException
    result = await TestSuite.filter(id=suite_id).delete()
    return ResultResponse[str](message="successful deleted testsuite!")
