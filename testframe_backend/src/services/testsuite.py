from tortoise.exceptions import DoesNotExist
from ..db.models import TestSuite, TestSuiteTaskId
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

    @staticmethod
    async def change_status(suite_id: int, status: int) -> int:
        """修改suite status

        Args:
            suite_id (str): 套件id
            status (int): 更新状态码
        Returns:
            int: 更新数量
        """
        suite = await TestSuite.filter(id=suite_id).update(status=status)
        return suite
