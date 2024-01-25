import asyncio, json
from fastapi import Request
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

    @staticmethod
    async def generate_run_data(request: Request) -> None:
        """生成推送数据"""
        counter = 0
        while True:
            if await request.is_disconnected():
                log.debug("Request disconnected")
                break
            if counter == 3:
                break
            await asyncio.sleep(5)  # 模拟耗时操作 @TODO 获取测试进度？
            event_data = {
                "id": counter,
                "event": "message",
                "retry": 1000,
                "data": json.dumps(dict(title="测试开始", description="擦擦擦擦拭")),
            }
            yield event_data
            counter += 1
