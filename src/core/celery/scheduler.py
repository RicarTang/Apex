# src/core/celery/custom_scheduler.py
import time
import json
import logging
from datetime import datetime
from celery.beat import Scheduler, ScheduleEntry
from celery.schedules import crontab
from sqlalchemy import text
from src.utils.sql_engine import engine
from src.utils.log_util import log


class DatabaseScheduleEntry(ScheduleEntry):
    """增强版任务条目，带详细日志"""

    def is_due(self):
        due, next_time = self.schedule.is_due(self.last_run_at)

        # 添加详细日志
        last_run = (
            self.last_run_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.last_run_at
            else "从未"
        )
        log.debug(f"任务: {self.name}")
        log.debug(f"  上次执行: {last_run}")
        log.debug(f"  是否到期: {due}")
        log.debug(f"  下次执行: {next_time} 秒后")

        return due, next_time


class DatabaseScheduler(Scheduler):
    """增强版数据库调度器，带详细诊断日志"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        log.info("=" * 50)
        log.info("初始化自定义调度器")

        self._schedule = {}
        self._last_update = 0
        self._sync_interval = 30
        self._last_sync = time.time()

        # 加载数据库任务
        self.update_schedule()

        log.info(f"初始加载 {len(self._schedule)} 个任务")
        log.info("=" * 50)

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
                try:
                    cron_parts = task.cron_expression.split()
                    new_schedule[task.name] = DatabaseScheduleEntry(
                        name=task.name,
                        task=task.task,
                        schedule=crontab(
                            minute=cron_parts[0],
                            hour=cron_parts[1],
                            day_of_month=cron_parts[2],
                            month_of_year=cron_parts[3],
                            day_of_week=cron_parts[4],
                        ),
                        kwargs=json.loads(task.task_kwargs) if task.task_kwargs else {},
                    )
                    log.info(f"添加任务: {task.name}, cron: {task.cron_expression}")
                except Exception as e:
                    log.error(f"添加任务 {task.name} 失败: {str(e)}")

            # 更新内存中的配置
            self._schedule = new_schedule
            self._last_update = time.time()
            log.info(f"成功加载 {len(new_schedule)} 个任务")
        except Exception as e:
            log.error(f"更新任务配置失败: {str(e)}")

    def tick(self):
        """每次调度循环执行"""
        log.debug("=" * 50)
        log.debug(f"开始调度周期 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

        # 记录所有任务状态
        for name, entry in self._schedule.items():
            due, next_time = entry.is_due()
            log.debug(f"任务: {name} - 到期: {due}, 下次: {next_time}s")

        # 调用父类方法执行任务
        result = super().tick()

        # 记录执行结果
        if result > 0:
            log.debug(f"下次调度在 {result} 秒后")
        else:
            log.debug("立即重新调度")

        log.debug("=" * 50)
        return result
