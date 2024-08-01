import json
from typing import Union, List, NamedTuple
from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet
from httpx import AsyncClient, TimeoutException, Response
from ...utils.exceptions.testcase import (
    RequestTimeOutException,
    AssertErrorException,
)
from ...db.models import TestCase
from ...utils.log_util import log


class TestCaseService:
    """测试用例服务"""

    @staticmethod
    async def add_testcase(testcase: Union[dict, NamedTuple]) -> QuerySet:
        """添加单条测试用例

        Args:
            testcase (Union[dict, NamedTuple]): 测试用例数据,导入时为具名元组,添加单条时是字典类型

        Returns:
            TestCase: _description_
        """
        if isinstance(testcase, tuple):
            result = await TestCase.create(**testcase._asdict())
        else:
            result = await TestCase.create(**testcase)
        return result

    @staticmethod
    async def add_testcase_from_list(testcases: List[NamedTuple]) -> None:
        """导入测试用例列表

        Args:
            testcases (List[NamedTuple]): namedtuple组成的列表
        """
        # 转换namedtuple列表为模型对象列表
        testcase_model_list = [TestCase(**testcase._asdict()) for testcase in testcases]
        await TestCase.bulk_create(testcase_model_list)

    @staticmethod
    async def execute_testcase(testcase: TestCase, current_env: str) -> Response:
        """执行单条测试用例

        Args:
            testcase (TestCase): Testcase模型对象
            current_env (str): 当前环境地址

        Raises:
            HTTPException: _description_
            RequestTimeOutException: 请求超时
            AssertErrorException: 断言错误
        Return:
            Response: httpx Response对象
        """
        async with AsyncClient(base_url=current_env) as client:
            body_date = None
            if testcase.request_param and testcase.request_param_type == "body":
                try:
                    body_date = json.loads(testcase.request_param)
                except json.JSONDecodeError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Request body type error!",
                    )
                log.debug(json.loads(testcase.request_param))

            try:
                # 请求
                res = await client.request(
                    method=testcase.api_method,
                    json=body_date,
                    url=testcase.api_path,
                )
            except TimeoutException:
                raise RequestTimeOutException
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request error!",
                )
            # 断言
            try:
                assert (
                    res.status_code == testcase.expect_code
                ), f"Assert error: response code {res.status_code} != expect code {testcase.expect_code}"
            except AssertionError as e:
                log.error(f"断言错误:{e}")
                raise AssertErrorException(
                    e,
                    dict(
                        code=res.status_code,
                        time=res.elapsed.total_seconds() * 1000,
                        headers=dict(res.headers),
                        body=res.json(),
                    ),
                )
            return res
