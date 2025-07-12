# 导入task模块
# from celery.beat import crontab
from .scheduler import DatabaseScheduler
imports = ("src.core.celery.task.testcase_task", "src.core.celery.task.scheduled_task","src.core.celery.scheduler")
# 使用utc时区
enable_utc = False
# 时区
timezone = "Asia/Shanghai"
# started状态显示
task_track_started = True
# 定时任务配置
# beat_schedule = {
#     'statistics-dashbord-data': {
#         'task': 'src.core.celery.task.scheduled_task.statistics_dashbord_data',  # task指向task name
#         'schedule': crontab(minute="*"),
#     }
# }
# 自定义调度器
beat_scheduler = DatabaseScheduler
