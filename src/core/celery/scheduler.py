"""自定义调度器"""

import json
from sqlalchemy import text
from celery.beat import crontab
from celery.signals import beat_init, beat_embedded_init
from src.utils.sql_engine import engine
from src.utils.log_util import log
from src.core.celery.celery_app import celery

# 全局内存存储任务配置
beat_schedule = {}


def parse_cron(expr: str) -> dict:
    """解析cron表达式为celery crontab格式"""
    parts = expr.split()
    return {
        "minute": parts[0],
        "hour": parts[1],
        "day_of_month": parts[2],
        "month_of_year": parts[3],
        "day_of_week": parts[4],
    }


@beat_init.connect
@beat_embedded_init.connect  # 兼容worker --beat
def load_tasks_on_beat_start(sender=None, **kwargs):
    """Beat启动时/独立或嵌入式从数据库加载所有任务"""
    global beat_schedule
    log.info(f"更新前 beat_schedule: {celery.conf.beat_schedule}")
    log.info("Beat初始化,从数据库中获取最新的task")
    beat_schedule.clear()
    sql_text = text("SELECT * FROM scheduled_task WHERE status = 1")
    try:
        with engine.connect() as db:
            tasks = db.execute(sql_text).fetchall()
    except Exception as e:
        log.error(f"数据库查询失败: {e}")
    else:
        # 添加/更新任务
        for task in tasks:
            beat_schedule[task.name] = {
                "task": task.task,
                "schedule": crontab(**parse_cron(task.cron_expression)),
                "kwargs": json.loads(task.task_kwargs) or {},
            }
    # 更新Beat配置
    celery.conf.beat_schedule = beat_schedule
    log.info(f"Beat初始化完成,从数据库中获取了最新的task:{celery.conf.beat_schedule}")
