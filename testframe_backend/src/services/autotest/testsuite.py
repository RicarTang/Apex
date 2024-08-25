import json
from typing import AsyncGenerator, Dict, Any
from fastapi import Request
from tortoise.exceptions import DoesNotExist
from ...db.models import TestSuite
from ...core.redis import RedisService
from ...utils.log_util import log
from ...utils.exceptions.testsuite import TestsuiteNotExistException


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
    async def get_redis_sse_subscribe(cls, task_id: str) -> dict:
        """从redis拿取sse推送订阅数据

        Args:
            task_id (str): celery task id

        Returns:
            dict: redis 订阅消息字典
        """
        key = task_id + "-sse_data"
        # 创建订阅者对象
        pubsub = await RedisService().aioredis_pool.pubsub()
        # 订阅频道
        await pubsub.subscribe(key)
        # 处理异步生成器
        async for message in pubsub.listen():
            if message["type"] == "message":
                # log.debug(message)
                return message

    @classmethod
    async def generate_sse_data(
        cls, request: Request, task_id: str
    ) -> AsyncGenerator[Dict,Any]:
        """生成推送数据

        Args:
            request (Request): _description_
            task_id (str): celery task id

        Yields:
            _type_: 返回字典数据
        """
        counter = 0

        while True:
            # 断开连接
            if await request.is_disconnected():
                log.debug("Request disconnected")
                break
            # 从对应的task_id拿取需要推送的状态
            send_data = await cls.get_redis_sse_subscribe(task_id)
            if send_data:
                # 有数据推送数据
                event_data = {
                    "id": counter,
                    "event": "message",
                    "retry": 1000,
                    "data": json.dumps(
                        dict(
                            task_id=task_id,
                            message=json.loads(send_data["data"]),
                        )
                    ),
                }
                yield event_data
                if json.loads(send_data["data"])["status"] == 1:
                    break
            counter += 1
