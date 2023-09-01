# from redis import asyncio as aioredis
from fastapi import Depends
# from redis.client import Redis
from aioredis.client import Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from config import config


async def aioredis_pool():
    """异步redis"""
    redis = Redis.from_url(config.REDIS_URL)
    return redis


async def init_cache(redis=Depends(aioredis_pool)):
    """初始化fastapi-cache2 Cache

    Args:
        redis (_type_, optional): _description_. Defaults to Depends(init_redis_pool).
    """
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache", expire=60)
