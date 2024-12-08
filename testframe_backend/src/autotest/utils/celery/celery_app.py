from celery import Celery
from .....config import config
from ..celery import celery_config


# 配置Celery
celery = Celery(
    "tasks",
    broker = config.CELERY_BROKER,  # Redis作为消息代理
    backend = config.CELERY_BACKEND,  # MySQL作为结果后端
)


# 指定celery配置
celery.config_from_object(celery_config)