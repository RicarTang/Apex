from typing import Optional
from fastapi import (
    APIRouter,
    Query,
)
from fastapi.encoders import jsonable_encoder
from tortoise.exceptions import DoesNotExist
from tortoise.transactions import in_transaction
from tortoise.query_utils import Prefetch
from ..db.models import TestSuite,TestCase
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
        await testsuite.testcase.add(testcase_result)
    return ResultResponse[testsuite_schema.TestSuiteTo](result=testsuite)


@router.get(
    "/getAll",
    summary="获取所有测试套件",
    # response_model=ResultResponse[testsuite_schema.TestSuitesTo],
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
    testsuite_list = await TestSuite.all().prefetch_related("testcase").offset(limit * (page - 1)).limit(limit)
    # log.debug(f"testsuite_list:{jsonable_encoder(testsuite_list[0])}")
    log.debug(f"{type(await TestSuite.all())}")
    total = await TestSuite.all().count()
    return testsuite_list
    # return ResultResponse[testsuite_schema.TestSuitesTo](
    #     result=testsuite_schema.TestSuitesTo(
    #         data=testsuite_list,
    #         page=page,
    #         limit=limit,
    #         total=total,
    #     )
    # )
    # return {
    #     "success": True,
    #     "message": "success",
    #     "result": {
    #         "page": 1,
    #         "limit": 10,
    #         "total": 2,
    #         "data": [
    #             {
    #                 "id": 2,
    #                 "created_at": "2023-09-22T10:43:32.671951+08:00",
    #                 "update_at": "2023-09-22T10:43:32.671981+08:00",
    #                 "suite_no": "1002",
    #                 "suite_title": "添加用户",
    #                 "remark": "添加用户测试套件",
    #                 "data": [
    #                     {
    #                         "id": 18,
    #                         "created_at": "2023-09-25T10:44:44.410192+08:00",
    #                         "update_at": "2023-09-25T10:44:44.410225+08:00",
    #                         "case_no": "1003",
    #                         "case_title": "密码错误登录",
    #                         "case_description": "测试密码错误时的登录场景",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 1,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{"username": "tang", "password": "1234567"}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 5,
    #                         "created_at": "2023-09-20T16:18:26.957573+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957583+08:00",
    #                         "case_no": "2002",
    #                         "case_title": "登录失败",
    #                         "case_description": "登录失败用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 0,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "1234567"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 4,
    #                         "created_at": "2023-09-20T16:18:26.957523+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957534+08:00",
    #                         "case_no": "2001",
    #                         "case_title": "登录成功",
    #                         "case_description": "登录成功用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 1,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "123456"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 1,
    #                         "response_to_redis": 1,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 3,
    #                         "created_at": "2023-09-20T16:18:26.957471+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957483+08:00",
    #                         "case_no": "1002",
    #                         "case_title": "登录失败",
    #                         "case_description": "登录失败用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 0,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "1234567"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 18,
    #                         "created_at": "2023-09-25T10:44:44.410192+08:00",
    #                         "update_at": "2023-09-25T10:44:44.410225+08:00",
    #                         "case_no": "1003",
    #                         "case_title": "密码错误登录",
    #                         "case_description": "测试密码错误时的登录场景",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 1,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{"username": "tang", "password": "1234567"}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 5,
    #                         "created_at": "2023-09-20T16:18:26.957573+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957583+08:00",
    #                         "case_no": "2002",
    #                         "case_title": "登录失败",
    #                         "case_description": "登录失败用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 0,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "1234567"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 4,
    #                         "created_at": "2023-09-20T16:18:26.957523+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957534+08:00",
    #                         "case_no": "2001",
    #                         "case_title": "登录成功",
    #                         "case_description": "登录成功用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 1,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "123456"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 1,
    #                         "response_to_redis": 1,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 3,
    #                         "created_at": "2023-09-20T16:18:26.957471+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957483+08:00",
    #                         "case_no": "1002",
    #                         "case_title": "登录失败",
    #                         "case_description": "登录失败用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 0,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "1234567"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 18,
    #                         "created_at": "2023-09-25T10:44:44.410192+08:00",
    #                         "update_at": "2023-09-25T10:44:44.410225+08:00",
    #                         "case_no": "1003",
    #                         "case_title": "密码错误登录",
    #                         "case_description": "测试密码错误时的登录场景",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 1,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{"username": "tang", "password": "1234567"}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 5,
    #                         "created_at": "2023-09-20T16:18:26.957573+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957583+08:00",
    #                         "case_no": "2002",
    #                         "case_title": "登录失败",
    #                         "case_description": "登录失败用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 0,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "1234567"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 4,
    #                         "created_at": "2023-09-20T16:18:26.957523+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957534+08:00",
    #                         "case_no": "2001",
    #                         "case_title": "登录成功",
    #                         "case_description": "登录成功用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 1,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "123456"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 1,
    #                         "response_to_redis": 1,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                     {
    #                         "id": 3,
    #                         "created_at": "2023-09-20T16:18:26.957471+08:00",
    #                         "update_at": "2023-09-20T16:18:26.957483+08:00",
    #                         "case_no": "1002",
    #                         "case_title": "登录失败",
    #                         "case_description": "登录失败用例",
    #                         "case_module": "登录",
    #                         "case_sub_module": None,
    #                         "case_is_execute": 0,
    #                         "api_path": "/user/login",
    #                         "api_method": "post",
    #                         "request_headers": None,
    #                         "request_param_type": "body",
    #                         "request_param": '{\n  "username": "tang",\n  "password": "1234567"\n}',
    #                         "expect_code": 200,
    #                         "expect_result": None,
    #                         "expect_data": None,
    #                         "request_to_redis": 0,
    #                         "response_to_redis": 0,
    #                         "case_editor": "thb",
    #                         "remark": None,
    #                     },
    #                 ],
    #             },
    #             {
    #                 "id": 1,
    #                 "created_at": "2023-09-22T10:42:49.332126+08:00",
    #                 "update_at": "2023-09-22T10:42:49.332156+08:00",
    #                 "suite_no": "1001",
    #                 "suite_title": "登录",
    #                 "remark": "登录测试套件",
    #                 "data": [],
    #             },
    #         ],
    #     },
    # }


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
