# from redis import asyncio as aioredis
from redis.client import Redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from config import config


async def init_redis_pool():
    """初始化redis连接池"""
    redis = Redis.from_url(config.REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache",expire=60)
