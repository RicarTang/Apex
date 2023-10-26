from fastapi import Depends
import asyncio
from aiohttp import ClientSession
from aioredis import Redis
from aiohttp.client_exceptions import ClientConnectionError
from ..cache import aioredis_pool


class ApiTestDependency:
    """api接口测试依赖项"""

    def __init__(
        self,
        current_env_name: str = "currentEnv",
        redis: Redis = Depends(aioredis_pool),
    ) -> None:
        self.redis = redis
        self.current_env_name = current_env_name

    async def get_current_env(self):
        """拿取当前环境变量"""
        try:
            current_env = await self.redis.get(self.current_env_name)
        except ClientConnectionError as e:
            raise e
        else:
            return current_env

    async def set_current_env(self, value: str):
        """设置当前环境变量

        Args:
            key (str): redis 键
            value (str): redis 值
            redis (Redis, optional): redis依赖
        """
        try:
            await self.redis.set(self.current_env_name, value)
        except Exception as e:
            raise e

    async def execute_one(self, method: str, url: str, expect_code: int):
        """执行单条测试用例

        Args:
            method (str): 请求方法
            url (str): 请求url
            expect_code (int): 断言状态码
        """
        async with ClientSession() as session:
            async with session.request(method, url) as resp:
                assert resp.status == expect_code
                return True
