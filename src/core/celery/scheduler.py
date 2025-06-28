"""自定义调度器"""

from sqlalchemy import text
from celery.beat import PersistentScheduler, crontab
from src.utils.sql_engine import engine
from src.config import config
from src.utils.log_util import log


class DatabaseScheduler(PersistentScheduler):
    """自定义调度器：从数据库加载任务配置，使用shelve文件保存执行状态"""

    def __init__(self, *args, **kwargs):
        """初始化调度器"""
        self.refresh_interval = config.CELERY_BEAT_CHECK_INTERVAL or self.max_interval
        self._last_refresh = None
        super().__init__(*args, **kwargs)

    def _parse_cron(self, expr: str) -> dict:
        """解析cron表达式"""
        parts = expr.split()
        return {
            "minute": parts[0],
            "hour": parts[1],
            "day_of_month": parts[2],
            "month_of_year": parts[3],
            "day_of_week": parts[4],
        }

    def _load_entries(self) -> dict:
        """从数据库加载任务配置"""
        sql_text = text("SELECT * FROM scheduled_task WHERE status = 1")
        entries = {}
        try:
            with engine.connect() as db:
                tasks = db.execute(sql_text).fetchall()
        except Exception as e:
            log.error(f"数据库查询失败: {e}")
        else:
            # 添加/更新任务
            for task in tasks:
                entries[task.name] = self.Entry(
                    name=task.name,
                    task=task.task,
                    schedule=crontab(**self._parse_cron(task.cron_expression)),
                    kwargs=task.task_kwargs or {},
                    app=self.app,
                )
        return entries

    # 定期刷新任务配置（不影响 PersistentScheduler 的状态存储）
    def sync(self):
        if self._should_refresh():
            try:
                log.info("开始从数据库同步task".center(30, "-"))
                self._last_refresh = self.app.now()
                new_entries = self._load_entries()
                self.update_from_dict(new_entries)  # 更新内存中的任务列表
                log.info("成功从数据库更新task任务".center(30, "-"))
            except Exception as e:
                log.error(f"自定义同步失败！{e}")
        super().sync()  # 调用父类方法处理状态持久化
        log.debug(
            f"任务状态更新: {[(entry.name,entry.last_run_at) for entry in self.schedule.values()]}"
        )

    def _should_refresh(self):
        if self._last_refresh is None:
            return True
        return (
            self.app.now() - self._last_refresh
        ).total_seconds() >= self.refresh_interval
