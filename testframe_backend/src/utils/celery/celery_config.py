from celery import Celery
from ....config import config


# 配置Celery
celery = Celery(
    "tasks",
    broker = config.CELERY_BROKER,  # Redis作为消息代理
    backend = config.CELERY_BACKEND,  # MySQL作为结果后端
)

# 指定包含 Celery 任务的模块
celery.conf.update(
    imports=("testframe_backend.src.utils.celery.task.testcase_task",),  # 需要导入task模块
    # 其他 Celery 配置项...
)