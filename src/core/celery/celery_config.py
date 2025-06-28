# 导入task模块
imports = ("src.core.celery.task.testcase_task", "src.core.celery.task.scheduled_task")
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
#         'schedule': crontab(hour="*/1",minute=0),  # 每个小时执行
#     }
# }
# 自定义调度器
beat_scheduler = "src.core.celery.scheduler.DatabaseScheduler"
