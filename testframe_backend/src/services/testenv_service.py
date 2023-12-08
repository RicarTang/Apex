from fastapi import Depends
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectionError
from ...src.core.cache import aioredis_pool


class TestEnvService:
    """测试环境服务"""

    @classmethod
    async def get_current_env(cls, current_env_name: str = "currentEnv"):
        """拿取平台当前环境变量"""
        async with aioredis_pool() as redis:
            try:
                current_env = await redis.get(current_env_name)
            except ClientConnectionError as e:
                raise e
            else:
                return current_env

    @classmethod
    async def set_current_env(cls, value: str):
        """设置当前环境变量

        Args:
            value (str): 环境变量值
        """
        async with aioredis_pool() as redis:
            try:
                await redis.set(cls.current_env_name, value)
            except Exception as e:
                raise e

    @classmethod
    async def execute_one(cls, method: str, url: str, expect_code: int):
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
