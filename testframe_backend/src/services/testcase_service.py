from typing import Union, List, NamedTuple
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet
from ..db.models import TestCase
from ..utils.log_util import log


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