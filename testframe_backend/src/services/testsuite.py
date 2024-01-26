import asyncio, json, queue
from fastapi import Request
from tortoise.exceptions import DoesNotExist
from ..db.models import TestSuite
from ..core.cache import RedisService
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


class TestSuiteSSEService:
    """测试套件sse推送服务"""

    @classmethod
    async def get_redis_sse_data(cls, task_id: str):
        """从redis拿取测试状态"""
        key = task_id + "sse_data"
        data = await RedisService.aio_lpop(key)
        return data

    @classmethod
    async def generate_sse_data(cls, request: Request, task_id: str) -> None:
        """生成推送数据"""
        counter = 0

        while True:
            # 断开连接
            if await request.is_disconnected():
                log.debug("Request disconnected")
                break
            # 从对应的task_id拿取需要推送的状态
            send_data = cls.get_redis_sse_data(task_id)
            if send_data:
                # 有数据推送数据
                event_data = {
                    "id": counter,
                    "event": "message",
                    "retry": 1000,
                    "data": json.dumps(dict(task_id=task_id, message=send_data)),
                }
                yield event_data
            await asyncio.sleep(2)  # 模拟耗时操作,给其他代码得到cpu的时间 @TODO 获取测试进度？
            counter += 1
