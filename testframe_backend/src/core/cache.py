from typing import Union, Any, Awaitable
from pathlib import Path
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from redis.client import Redis
from redis.asyncio import Redis as AioRedis

# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
from ...config import config


class RedisService:
    """redis服务"""

    def __init__(self, url: Union[str, Path] = config.REDIS_URL) -> None:
        self.url = url

    @asynccontextmanager
    async def aioredis_pool(self, **kwargs) -> AioRedis:
        """异步redis上下文管理器服务"""
        redis = aioredis.from_url(
            self.url,
            encoding="utf-8",
            decode_responses=True,  # 自动解码response
            **kwargs,
        )
        try:
            yield redis
        finally:
            await redis.aclose()

    def redis_pool(self, **kwargs) -> Redis:
        """同步redis pool"""
        redis: Redis = Redis.from_url(
            self.url,
            # encoding="utf-8",
            # decode_responses=True,  # 自动解码response
            **kwargs,
        )
        try:
            return redis
        finally:
            redis.close()

    async def aio_set(
        self,
        key: Union[str, bytes, memoryview],
        value: Union[str, bytes, memoryview, int, float],
        **kwargs: Any,
    ) -> bool:
        """异步set

        Args:
            key (Union[str, bytes, memoryview]): _description_
            value (Union[str, bytes, memoryview, int, float]): _description_
            kwargs:
                ex:
                px:
                nx:
                xx:
                keepttl:
                get:
                exat:
                pxat:
                具体参考:https://redis-py.readthedocs.io/en/stable/commands.html#redis.commands.core.CoreCommands.set
        Raises:
            e: _description_

        Returns:
            bool: _description_
        """
        async with self.aioredis_pool() as redis:
            try:
                return await redis.set(name=key, value=value, **kwargs)
            except Exception as e:
                raise e

    async def aio_get(
        self, key: Union[str, bytes, memoryview]
    ) -> Union[Any, Awaitable]:
        """异步get

        Args:
            key (Union[str, bytes, memoryview]): _description_

        Raises:
            e: _description_

        Returns:
            Union[Any, Awaitable]: _description_
        """
        async with self.aioredis_pool() as redis:
            try:
                return await redis.get(name=key)
            except Exception as e:
                raise e

    def get(self, key: Union[str, bytes, memoryview]) -> Any:
        """同步get

        Args:
            key (Union[str, bytes, memoryview]): _description_

        Returns:
            Any: _description_
        """
        try:
            return self.redis_pool().get(key)
        except Exception as e:
            raise e

    def set(
        self,
        key: Union[str, bytes, memoryview],
        value: Union[str, bytes, memoryview, int, float],
        **kwargs: Any,
    ) -> bool:
        """同步set

        Args:
            key (Union[str, bytes, memoryview]): _description_
            value (Union[str, bytes, memoryview, int, float]): _description_
            kwargs:
                ex:
                px:
                nx:
                xx:
                keepttl:
                get:
                exat:
                pxat:
                具体参考:https://redis-py.readthedocs.io/en/stable/commands.html#redis.commands.core.CoreCommands.set
        Raises:
            e: _description_

        Returns:
            bool: _description_
        """
        try:
            return self.redis_pool().set(name=key, value=value, **kwargs)
        except Exception as e:
            raise e

    def getdel(self, key: Union[str, bytes, memoryview]) -> Any:
        """同步getdel

        Args:
            key (Union[str, bytes, memoryview]): _description_

        Returns:
            Any: _description_
        """
        try:
            return self.redis_pool().getdel(key)
        except Exception as e:
            raise e
