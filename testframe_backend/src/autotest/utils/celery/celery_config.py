from celery import Celery
from .....config import config


# 配置Celery
celery = Celery(
    "tasks",
    broker = config.CELERY_BROKER,  # Redis作为消息代理
    backend = config.CELERY_BACKEND,  # MySQL作为结果后端
)
# 指定包含 Celery 任务的模块
celery.conf.update(
    imports=("testframe_backend.src.autotest.utils.celery.task.testcase_task",),  # 需要导入task模块
    enable_utc=True,
    timezone="Asia/Shanghai",  # 时区修改为上海
    task_track_started=True,  # started状态显示
)