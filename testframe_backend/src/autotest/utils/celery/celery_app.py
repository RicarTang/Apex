from celery import Celery
from .....config import config
from ....db.models import ScheduledTask


# 配置Celery
celery = Celery(
    "tasks",
    broker = config.CELERY_BROKER,  # Redis作为消息代理
    backend = config.CELERY_BACKEND,  # MySQL作为结果后端
)


# 指定celery配置
celery.config_from_object("celery_config")

@celery.on_after_configure.connect
def load_tasks_from_db(sender, **kwargs):
    """
    Celery 配置完成后，动态加载数据库中激活的任务
    """
    pass
    # try:
    #     # 查询所有激活的任务
    #     active_tasks = await ScheduledTask.filter
    #     active_tasks = session.query(ScheduledTask).filter(ScheduledTask.is_active == True).all()
    #     for task in active_tasks:
    #         sender.add_periodic_task(
    #             task.interval,
    #             execute_test.s(task.task_name),
    #             name=f"task_{task.id}"
    #         )
    #     print(f"Loaded {len(active_tasks)} tasks from the database.")
    # finally:
    #     session.close()