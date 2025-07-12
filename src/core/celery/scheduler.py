from celery.beat import Scheduler, ScheduleEntry
from celery.schedules import crontab
from sqlalchemy import text
from src.utils.sql_engine import engine
from src.utils.log_util import log
import json


class DatabaseScheduleEntry(ScheduleEntry):
    """兼容原生的任务条目"""

    def __init__(
        self,
        name=None,
        task=None,
        schedule=None,
        args=(),
        kwargs=None,
        options=None,
        last_run_at=None,
        total_run_count=None,
    ):
        super().__init__(
            name=name,
            task=task,
            schedule=schedule,
            args=args,
            kwargs=kwargs or {},
            options=options or {},
            last_run_at=last_run_at,
            total_run_count=total_run_count,
        )

    def is_due(self):
        """计算任务是否到期（复用原生逻辑）"""
        return self.schedule.is_due(self.last_run_at)

    def __next__(self):
        """准备下一次执行（复用原生逻辑）"""
        self.last_run_at = self.now()
        return self


class DatabaseScheduler(Scheduler):
    """完全兼容原生接口的数据库调度器"""

    def __init__(self, app, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self._initialized = False
        self.schedule = {}  # 必须使用 self.schedule

    def setup_schedule(self):
        """初始化方法，Beat启动时调用"""
        if not self._initialized:
            log.info("=" * 50)
            log.info("初始化数据库调度器")

            # 从数据库加载任务
            self.load_tasks_from_db()

            log.info(f"已加载 {len(self.schedule)} 个任务")
            log.info("=" * 50)
            self._initialized = True

    def load_tasks_from_db(self):
        """从数据库加载任务"""
        try:
            # 查询所有启用的任务
            sql = text("SELECT * FROM scheduled_task WHERE status = 1")
            with engine.connect() as conn:
                tasks = conn.execute(sql).fetchall()

            # 清空当前配置
            self.schedule.clear()

            # 添加任务
            for task in tasks:
                try:
                    cron_parts = task.cron_expression.split()
                    self.schedule[task.name] = DatabaseScheduleEntry(
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
                        last_run_at=None,
                    )
                    log.info(f"添加任务: {task.name}")
                except Exception as e:
                    log.error(f"添加任务 {task.name} 失败: {str(e)}")
        except Exception as e:
            log.error(f"从数据库加载任务失败: {str(e)}")

    def sync(self):
        """同步任务状态到数据库（可选）"""
        # 可以在这里实现状态持久化
        pass

    def close(self):
        """关闭调度器"""
        self.sync()
        super().close()
