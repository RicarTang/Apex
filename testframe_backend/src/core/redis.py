from typing import Union, Any, Awaitable, Optional, List
from pathlib import Path

# from contextlib import asynccontextmanager
from redis import ConnectionPool
from redis.client import Redis
from redis.asyncio import Redis as AioRedis, ConnectionPool as AioConnectionPool
from .custom_metaclass import Singleton

# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisServiceBackend
from ...config import config


class RedisService(metaclass=Singleton):
    """redis服务"""

    def __init__(self, url: Union[str, Path] = config.REDIS_URL) -> None:
        self.url = url
        # 实例两种类型redis连接池避免多次调用导致的多次实例化
        self.aioredis_pool = self.__aioredis_pool()
        self.redis_pool = self.__redis_pool()


    def __aioredis_pool(self) -> AioRedis:
        """初始化异步redis poll"""
        pool: AioConnectionPool = AioConnectionPool.from_url(
            self.url,
            # encoding="utf-8",
            # decode_responses=True,  # 自动解码response
        )
        redis = AioRedis.from_pool(pool)
        return redis

    def __redis_pool(self) -> Redis:
        """初始化同步redis pool"""
        pool: ConnectionPool = ConnectionPool.from_url(
            self.url,
            # encoding="utf-8",
            # decode_responses=True,  # 自动解码response
        )
        redis = Redis.from_pool(pool)
        return redis
