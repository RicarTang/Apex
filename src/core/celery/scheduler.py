# src/core/celery/simple_scheduler.py
from celery.beat import Scheduler
from celery.schedules import crontab
from sqlalchemy import text
from src.utils.sql_engine import engine
from src.utils.log_util import log
import json
import time


class DynamicScheduler(Scheduler):
    """简化但可靠的动态调度器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.info("初始化调度器")
        self.schedule = {}
        self.last_update = time.time()
        self.update_interval = 300  # 5分钟更新一次

        # 加载初始任务
        self.update_schedule()

    def update_schedule(self):
        """从数据库更新任务配置"""
        try:
            log.info("更新任务配置")
            new_schedule = {}

            # 从数据库加载任务
            sql = text("SELECT * FROM scheduled_task WHERE status = 1")
            with engine.connect() as conn:
                tasks = conn.execute(sql).fetchall()

            for task in tasks:
                try:
                    cron_parts = task.cron_expression.split()
                    new_schedule[task.name] = {
                        "task": task.task,
                        "schedule": crontab(
                            minute=cron_parts[0],
                            hour=cron_parts[1],
                            day_of_month=cron_parts[2],
                            month_of_year=cron_parts[3],
                            day_of_week=cron_parts[4],
                        ),
                        "kwargs": (
                            json.loads(task.task_kwargs) if task.task_kwargs else {}
                        ),
                    }
                    log.info(f"添加任务: {task.name}")
                except Exception as e:
                    log.error(f"添加任务失败: {str(e)}")

            # 更新配置
            self.schedule = new_schedule
            log.info(f"成功更新 {len(new_schedule)} 个任务")
        except Exception as e:
            log.error(f"更新任务失败: {str(e)}")

    def tick(self):
        """核心调度方法"""
        # 定期更新任务
        if time.time() - self.last_update > self.update_interval:
            self.update_schedule()
            self.last_update = time.time()

        # 返回父类方法
        return super().tick()
