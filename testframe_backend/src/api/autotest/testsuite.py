from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Query, HTTPException, status, Request
from typing_extensions import Annotated
from pydantic import StringConstraints
from fastapi.encoders import jsonable_encoder
from sse_starlette.sse import EventSourceResponse
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction
from celery.result import AsyncResult

from ...schemas.autotest import testsuite
from ...db.models import TestSuite, TestCase, TestSuiteTaskId
from ...schemas import ResultResponse
from ...utils.log_util import log
from ...utils.exceptions.testsuite import TestsuiteNotExistException
from ...utils.exceptions.testenv import CurrentTestEnvNotSetException
from ...autotest.utils.celery.task.testcase_task import task_test
from ...services.autotest.testenv import TestEnvService
from ...services.autotest.testsuite import TestSuiteSSEService
from ...core.redis import RedisService


router = APIRouter()


@router.post(
    "/add",
    summary="添加测试套件",
    response_model=ResultResponse[testsuite.TestSuiteTo],
)
async def add_testsuite(body: testsuite.TestSuiteIn):
    """新增测试套件"""
    async with in_transaction():
        # 新增
        result = await TestSuite.create(
            **body.model_dump(exclude_unset=True, exclude=["testcase_ids"])
        )
        # 判断关联用例
        if body.testcase_ids:
            testcases_result = await TestCase.filter(id__in=body.testcase_ids).all()
            await result.testcases.add(*testcases_result)
            # 查询关联用例
            await result.fetch_related("testcases")
    return ResultResponse[testsuite.TestSuiteTo](result=result)


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
        await query.prefetch_related(
            "testcases", "task_id"
        )  # 使用prefetch_related预取关联的testcase列表
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
async def run_testsuite(body: testsuite.RunSuiteIn):
    try:
        result = await TestSuite.get(id=body.suite_id).prefetch_related("testcases")
    except DoesNotExist:
        raise TestsuiteNotExistException
    if not await TestEnvService().aio_get_current_env():
        raise CurrentTestEnvNotSetException
    task: AsyncResult = task_test.apply_async(
        [
            jsonable_encoder(testsuite.TestSuiteTo.model_validate(result).testcases),
            body.suite_id,
        ],
    )  # 将Celery任务发送到消息队列,并传递测试数据
    # 保存对应的suite与task id
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
    "/runState",
    summary="推送套件运行状态",
)
async def sse_run_state(request: Request, task_id: str):
    """使用sse推送运行状态"""
    return EventSourceResponse(TestSuiteSSEService.generate_sse_data(request, task_id))


@router.delete(
    "/{suite_ids}",
    summary="删除测试套件",
    response_model=ResultResponse[None],
)
async def delete_testsuite(
    suite_ids: Annotated[
        str, StringConstraints(strip_whitespace=True, pattern=r"^\d+(,\d+)*$")
    ]
):
    """删除测试套件"""
    source_ids_list = suite_ids.split(",")
    delete_count = await TestSuite.filter(id__in=source_ids_list).delete()
    if not delete_count:
        raise TestsuiteNotExistException
    return ResultResponse[None](message="successful deleted testsuite!")


@router.get(
    "/{suite_id}",
    summary="获取指定testsuite",
    response_model=ResultResponse[testsuite.TestSuiteTo],
)
async def get_testsuite(suite_id: int):
    """获取指定测试套件"""
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
    """更新测试套件数据"""
    suite = await TestSuite.get_or_none(id=suite_id).prefetch_related("testcases")
    if not suite:
        raise TestsuiteNotExistException
    async with in_transaction():
        # 更新
        await TestSuite.filter(id=suite_id).update(
            **body.model_dump(
                exclude_unset=True,
                exclude=["testcase_ids"]
                # by_alias=True,
            )
        )
        # 更新关联用例
        if body.testcase_ids:
            # 获取接口请求用例列表
            case_list = await TestCase.filter(id__in=body.testcase_ids).all()
            # 获取请求套件的用例列表
            current_suite_case_list = await suite.testcases.all()
            log.debug(current_suite_case_list)

            # 确定需要添加和需要移除的ID
            case_ids_to_add = list(set(case_list) - set(current_suite_case_list))
            case_ids_to_remove = list(set(current_suite_case_list) - set(case_list))
            log.debug(f"toadd:{case_ids_to_add},toremove:{case_ids_to_remove}")
            # 添加/删除
            await suite.testcases.add(*case_ids_to_add)
            if case_ids_to_remove:
                await suite.testcases.remove(*case_ids_to_remove)
        # 刷新
        await suite.refresh_from_db()
        return ResultResponse[testsuite.TestSuiteTo](result=suite)
