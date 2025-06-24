"""自定义调度器"""

from time import monotonic
from sqlalchemy import text
from celery.beat import PersistentScheduler
from src.utils.sql_engine import engine
from src.config import config


class DatabaseScheduler(PersistentScheduler):
    """自定义调度器：从数据库加载任务配置，使用shelve文件保存执行状态"""

    def __init__(self, *args, **kwargs):
        """初始化调度器，设置数据库连接和检查间隔"""
        self.db_connection = engine.connect()
        self.db_check_interval = config.CELERY_BEAT_CHECK_INTERVAL or self.max_interval
        self.last_db_check = 0
        super().__init__(*args, **kwargs)

    def setup_schedule(self):
        """设置调度计划"""
        super().setup_schedule()
        self._load_tasks_from_db()
        self.last_db_check = monotonic()

    def _load_tasks_from_db(self):
        """从数据库加载任务配置"""
        sql_text = text("SELECT * FROM scheduled_task WHERE status = 1")
        try:
            tasks = self.db_connection.execute(sql_text).fetchall()
        except Exception as e:
            self.logger.error(f"数据库查询失败: {e}")
        else:
            # 添加/更新任务
            for task in tasks:
                entry = self.Entry(
                    name=task.name,
                    task=task.task,
                    schedule=task.cron_expression,
                    kwargs=task.task_kwargs or {},
                )

                if task.name in self.schedule:
                    self.schedule[task.name].update(entry)
                else:
                    self.schedule[task.name] = entry
        

    def tick(self, *args, **kwargs):
        """重写tick方法，增加数据库检查逻辑"""
        delay = super().tick(*args, **kwargs)

        # 周期性检查数据库
        now = monotonic()
        if now - self.last_db_check > self.db_check_interval:
            try:
                self._load_tasks_from_db()
                self.last_db_check = now
                self.logger.info("Database tasks reloaded")
            except Exception as e:
                self.logger.error(f"Failed to reload database tasks: {e}")

        return delay

    def close(self):
        """添加数据库连接的断开逻辑"""
        if self.db_connection:
            self.db_connection.close()
        super().close()
