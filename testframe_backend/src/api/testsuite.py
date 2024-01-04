from typing import Optional
from datetime import datetime
from fastapi import (
    APIRouter,
    Query,
)
from fastapi.encoders import jsonable_encoder
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction
from celery.result import AsyncResult
from ..db.models import TestSuite, TestCase, TestSuiteTaskId
from ..schemas import ResultResponse, testsuite
from ..utils.log_util import log
from ..utils.exceptions.testsuite import TestsuiteNotExistException
from ..utils.exceptions.testenv import CurrentTestEnvNotSetException
from ..autotest.utils.celery.task.testcase_task import task_test
from ..services.testenv import TestEnvService


router = APIRouter()


@router.post(
    "/add",
    summary="添加测试套件",
    response_model=ResultResponse[testsuite.TestSuiteTo],
)
async def add_testsuite(body: testsuite.TestSuiteIn):
    """新增测试套件

    Args:
        body (testsuite.TestSuiteIn): 包含测试套件信息的请求体

    Returns:
        ResultResponse[testsuite.TestSuiteTo]: 添加成功后的测试套件信息
    """
    async with in_transaction():
        try:
            testsuite = await TestSuite.create(**body.dict())
            testcases_result = await TestCase.filter(id__in=body.testcase_id).all()
            await testsuite.testcases.add(*testcases_result)
            await testsuite.fetch_related("testcases")
        except Exception as e:
            log.error(f"事务操作失败：{e}")
    return ResultResponse[testsuite.TestSuiteTo](result=testsuite)


@router.get(
    "/list",
    summary="获取测试套件列表",
    response_model=ResultResponse[testsuite.TestSuitesTo],
)
async def get_all_testsuite(
    suite_title: Optional[str] = Query(
        default=None, alias="suiteTitle", description="套件名称筛选"
    ),
    suite_no: Optional[str] = Query(
        default=None, alias="suiteNo", description="套件编号筛选"
    ),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取所有测试套件"""
    filters = {}
    if suite_title:
        filters["suite_title__icontains"] = suite_title
    if suite_no:
        filters["suite_no__icontains"] = suite_no
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
    query = TestSuite.filter(**filters)  
    suite_list = (
        await query.prefetch_related("testcases", "task_id")  # 使用prefetch_related预取关联的testcase列表
        .offset(limit * (page - 1))
        .limit(limit)
        .all()
    )
    total = await query.count()
    return ResultResponse[testsuite.TestSuitesTo](
        result=testsuite.TestSuitesTo(
            data=suite_list,
            page=page,
            limit=limit,
            total=total,
        )
    )


@router.get(
    "/testResult",
    summary="测试运行结果",
)
async def test_run_result(task_id: str):
    result = AsyncResult(task_id)
    return {"task_id": task_id, "status": result.status, "result": result.result}


@router.post(
    "/run",
    summary="运行测试套件",
    response_model=ResultResponse[dict],
)
async def run_testsuite(body: testsuite.TestSuiteId):
    try:
        result = await TestSuite.get(id=body.suite_id).prefetch_related("testcases")
    except DoesNotExist:
        raise TestsuiteNotExistException
    if not await TestEnvService().aio_get_current_env():
        raise CurrentTestEnvNotSetException
    task: AsyncResult = task_test.delay(
        testsuite_data=jsonable_encoder(
            ResultResponse[testsuite.TestSuiteTo](result=result).result.testcases
        )
    )  # 将Celery任务发送到消息队列,并传递测试数据
    # 对应保存suite与task id
    suite_task_id = await TestSuiteTaskId.get_or_none(testsuite_id=body.suite_id)
    if suite_task_id:
        suite_task_id.task_id = task.id
        await suite_task_id.save()
    else:
        await TestSuiteTaskId.create(testsuite_id=body.suite_id, task_id=task.id)
    return ResultResponse[dict](
        result={"message": "Tests are running in the background.", "task_id": task.id}
    )


@router.get(
    "/{suite_id}",
    summary="获取指定testsuite",
    response_model=ResultResponse[testsuite.TestSuiteTo],
)
async def get_testsuite(suite_id: int):
    """获取指定测试套件

    Args:
        suite_id (int): _description_
    """
    try:
        result = await TestSuite.get(id=suite_id).prefetch_related(
            "testcases", "task_id"
        )
    except DoesNotExist:
        raise TestsuiteNotExistException
    return ResultResponse[testsuite.TestSuiteTo](result=result)


@router.put(
    "/{suite_id}",
    summary="更新测试套件",
    response_model=ResultResponse[testsuite.TestSuiteTo],
)
async def update_testsuite(suite_id: int, body: testsuite.TestSuiteIn):
    """更新测试套件数据

    Args:
        suite_id (int): _description_
        body (testsuite.TestSuiteIn): _description_
    """
    if not await TestSuite.filter(id=suite_id).exists():
        raise TestsuiteNotExistException
    result = await TestSuite.filter(id=suite_id).update(**body.dict(exclude_unset=True))
    log.debug(f"update更新{result}条数据")
    return ResultResponse[testsuite.TestSuiteTo](
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
