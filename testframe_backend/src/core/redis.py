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

    def aioredis_pool(self, **kwargs) -> AioRedis:
        """异步redis poll"""
        pool: AioConnectionPool = AioConnectionPool.from_url(
            self.url,
            encoding="utf-8",
            decode_responses=True,  # 自动解码response
            **kwargs,
        )
        redis = AioRedis.from_pool(pool)
        return redis

    def redis_pool(self, **kwargs) -> Redis:
        """同步redis pool"""
        pool: ConnectionPool = ConnectionPool.from_url(
            self.url,
            # encoding="utf-8",
            # decode_responses=True,  # 自动解码response
            **kwargs,
        )
        redis = Redis.from_pool(pool)
        return redis
