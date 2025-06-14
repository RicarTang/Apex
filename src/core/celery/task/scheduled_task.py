from tortoise import run_async
from celery.schedules import crontab
from ..celery_app import celery
from .....db.models import ScheduledTask
from .....utils.log_util import log
from .....utils.enum import BoolEnum


@celery.on_after_configure.connect
def load_tasks_from_db(sender, **kwargs):
    """
    Celery 配置完成后，动态加载数据库中激活的任务
    """

    async def load_task():

        try:
            # 查询所有激活的任务
            active_tasks = await ScheduledTask.filter(enabled=BoolEnum.TRUE).all()
            # 添加所有定时任务
            for task in active_tasks:
                cron_parts = task.schedule.split()
                # 只支持简单的5字段CRON表达式
                if len(cron_parts) == 5:
                    minute, hour, day_of_month, month, day_of_week = cron_parts
                    sender.add_periodic_task(
                        crontab(
                            minute=minute,
                            hour=hour,
                            day_of_week=day_of_week,
                            day_of_month=day_of_month,
                            month=month,
                        ),
                        execute_test.s(task.task_name),
                        name=task.task_name,
                    )
                else:
                    log.error("只支持简单的5字段CRON表达式！")
                    # raise 
            log.info(f"已从数据库加载了 {len(active_tasks)} 个定时任务")
        except Exception as e:
            log.error(f"从数据库加载定时任务失败！{e}")

    run_async(load_task())


@celery.task
def execute_test():
    log.debug("测试定时任务")


@celery.task
def delete_allure():
    # @TODO 定期删除TestSuiteTaskId表中没有的allure目录
    pass
