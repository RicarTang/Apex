import httpx
from ...src.core.cache import aioredis_pool


class TestEnvService:
    """测试环境服务"""

    @staticmethod
    async def get_current_env(current_env_name: str = "currentEnv"):
        """redis读取平台当前环境变量"""
        async with aioredis_pool() as redis:
            current_env = await redis.get(current_env_name)
            return current_env

    @staticmethod
    async def set_current_env(current_env_name: str, value: str):
        """设置当前环境变量

        Args:
            value (str): 环境变量值
        """
        async with aioredis_pool() as redis:
            await redis.set(current_env_name, value)

    @staticmethod
    async def execute_one(method: str, url: str, expect_code: int):
        """执行单条测试用例(@TODO 待完善输入用例参数)

        Args:
            method (str): 请求方法
            url (str): 请求url
            expect_code (int): 断言状态码
        """
        async with httpx.AsyncClient() as client:
            res = await client.request(method=method, url=url)
            try:
                assert res.status_code == expect_code
                return True
            except AssertionError:
                return False
