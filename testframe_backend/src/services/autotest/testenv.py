# import httpx
# from ...core.redis import RedisService


# class TestEnvService:
#     """测试环境服务"""

#     def __init__(self, current_env_name: str = "currentEnv") -> None:
#         self.current_env_name = current_env_name

#     async def aio_get_current_env(self):
#         """redis异步读取平台当前环境变量"""
#         current_env = await RedisService().aioredis_pool.get(self.current_env_name)
#         return current_env

#     def get_current_env(self):
#         """redis同步读取平台当前环境变量"""
#         current_env = RedisService().redis_pool.get(self.current_env_name)
#         return current_env

#     async def aio_set_current_env(self, value: str) -> bool:
#         """设置当前环境变量

#         Args:
#             value (str): 环境变量值
#         """
#         return await RedisService().aioredis_pool.set(self.current_env_name, value)

#     @staticmethod
#     async def execute_one(method: str, url: str, expect_code: int):
#         """执行单条测试用例(@TODO 待完善输入用例参数)

#         Args:
#             method (str): 请求方法
#             url (str): 请求url
#             expect_code (int): 断言状态码
#         """
#         async with httpx.AsyncClient() as client:
#             res = await client.request(method=method, url=url)
#             try:
#                 assert res.status_code == expect_code
#                 return True
#             except AssertionError:
#                 return False
