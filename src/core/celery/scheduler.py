# src/core/celery/custom_scheduler.py
import json
import time
from celery.beat import Scheduler, ScheduleEntry
from celery.schedules import crontab
from sqlalchemy import text
from src.utils.sql_engine import engine
from src.utils.log_util import log



class DatabaseScheduler(Scheduler):
    """基于数据库的自定义调度器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._schedule = {}
        self._last_update = 0
        self._schedule_changed = False
        self._sync_interval = 30  # 每30秒同步一次数据库
        self._last_sync = time.time()
        self.update_schedule()

    def update_schedule(self):
        """从数据库更新任务配置"""
        log.info("从数据库更新任务配置")
        try:
            # 查询所有启用的任务
            sql = text("SELECT * FROM scheduled_task WHERE status = 1")
            with engine.connect() as conn:
                tasks = conn.execute(sql).fetchall()

            # 构建新的任务配置
            new_schedule = {}
            for task in tasks:
                cron_parts = task.cron_expression.split()
                new_schedule[task.name] = {
                    "name": task.name,
                    "task": task.task,
                    "schedule": crontab(
                        minute=cron_parts[0],
                        hour=cron_parts[1],
                        day_of_month=cron_parts[2],
                        month_of_year=cron_parts[3],
                        day_of_week=cron_parts[4],
                    ),
                    "kwargs": json.loads(task.kwargs) if task.kwargs else {},
                }

            # 更新内存中的配置
            self._schedule = new_schedule
            self._last_update = time.time()
            self._schedule_changed = True
            log.info(f"已加载 {len(new_schedule)} 个任务")
        except Exception as e:
            log.error(f"更新任务配置失败: {str(e)}")

    def sync(self):
        """同步配置到持久化存储（可选）"""
        # 这里可以添加持久化逻辑，但非必需
        self._schedule_changed = False

    def schedule_changed(self):
        """检查配置是否发生变化"""
        # 定期检查数据库更新
        current_time = time.time()
        if current_time - self._last_sync > self._sync_interval:
            self.update_schedule()
            self._last_sync = current_time
            return True

        return self._schedule_changed

    def get_schedule(self):
        """获取当前任务配置"""
        return self._schedule

    def set_schedule(self, schedule):
        """设置任务配置（用于API更新）"""
        self._schedule = schedule
        self._schedule_changed = True

    def close(self):
        """关闭调度器"""
        self.sync()
        super().close()

    def add_task(self, task):
        """添加单个任务"""
        cron_parts = task.cron_expression.split()
        self._schedule[task.name] = {
            "name": task.name,
            "task": task.task,
            "schedule": crontab(
                minute=cron_parts[0],
                hour=cron_parts[1],
                day_of_month=cron_parts[2],
                month_of_year=cron_parts[3],
                day_of_week=cron_parts[4],
            ),
            "kwargs": json.loads(task.kwargs) if task.kwargs else {},
        }
        self._schedule_changed = True

    def remove_task(self, task_name):
        """移除任务"""
        if task_name in self._schedule:
            del self._schedule[task_name]
            self._schedule_changed = True
