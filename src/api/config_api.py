import json
from typing import Optional, Union
from fastapi import APIRouter, Query, Depends
from tortoise.exceptions import DoesNotExist
from config import config
from ..core.cache import aioredis_pool
from ..db.models import TestEnv
from ..schemas import ResultResponse
from ..utils.log_util import log
from ..utils.load_file_util import File


router = APIRouter()


@router.post(
    "/setConfig",
    summary="设置配置信息",
)
async def set_config(redis=Depends(aioredis_pool)):
    pass


# except:
#     config_load = await File.loadyaml(config.TEST_CONFIG_PATH)
#     log.debug(f"redis未存储config配置,set配置{config_load}")
#     await redis.set("config", json.dumps(config_load))


@router.get(
    "/getConfig",
    summary="获取当前配置",
    response_model=ResultResponse[dict],
)
async def get_config(redis=Depends(aioredis_pool)):
    """获取test配置信息

    Args:
        redis (_type_, optional): _description_. Defaults to Depends(aioredis_pool).

    Returns:
        _type_: _description_
    """
    config_redis = await redis.get("config")
    try:
        config_redis = json.loads(config_redis)
    except TypeError:
        pass
    log.debug(f"config: {config_redis}")
    return ResultResponse[dict](result=config_redis)
