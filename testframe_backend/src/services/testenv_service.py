from fastapi import Depends
from aiohttp import ClientSession
from aioredis import Redis
from aiohttp.client_exceptions import ClientConnectionError
from ...src.core.cache import aioredis_pool


class TestEnvService:
    """测试环境服务"""

    def __init__(
        self,
        current_env_name: str = "currentEnv"
    ) -> None:
        self.current_env_name = current_env_name


    @property
    async def get_current_env(self):
        """拿取平台当前环境变量"""
        async with aioredis_pool() as redis:
            try:
                current_env = await redis.get(self.current_env_name)
            except ClientConnectionError as e:
                raise e
            else:
                return current_env

    async def set_current_env(self, value: str):
        """设置当前环境变量

        Args:
            value (str): 环境变量值
        """
        async with aioredis_pool() as redis:
            try:
                await redis.set(self.current_env_name, value)
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
