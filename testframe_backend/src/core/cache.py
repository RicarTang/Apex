from fastapi import Depends
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
from ...config import config

@asynccontextmanager
async def aioredis_pool():
    """异步redis上下文管理器服务"""
    redis = await aioredis.from_url(
        config.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,  # 自动解码response
    )
    try:
        yield redis
    finally:
        await redis.close()


async def init_cache(redis=Depends(aioredis_pool)):
    """初始化fastapi-cache2 Cache

    Args:
        redis (_type_, optional): _description_. Defaults to Depends(init_redis_pool).
    """
    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache", expire=60)
