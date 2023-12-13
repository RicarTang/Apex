from typing import Union, List, NamedTuple
from tortoise.exceptions import DoesNotExist
from ..db.models import TestSuite
from ..utils.log_util import log
from ..utils.exceptions.testsuite import TestsuiteNotExistException


class TestSuiteService:
    """测试套件服务"""

    @staticmethod
    async def get_suite_by_id(suite_id: int) -> TestSuite:
        """根据id获取testsuite

        Args:
            suite_id (int): 套件id

        Returns:
            TestSuite: TestSuite对象
        """
        try:
            result = await TestSuite.get(id=suite_id).prefetch_related("testcases")
            return result
        except DoesNotExist:
            raise TestsuiteNotExistException
        except Exception as e:
            raise e
