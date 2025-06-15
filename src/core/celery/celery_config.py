from celery.schedules import crontab
# 导入task模块
imports=("src.core.celery.task.testcase_task","src.core.celery.task.scheduled_task")
# 使用utc时区
enable_utc=True
# 时区
timezone="Asia/Shanghai"
# started状态显示
task_track_started=True
# 定时任务配置
beat_schedule = {
    'statistics-dashbord-data': {
        'task': 'src.core.celery.task.scheduled_task.statistics_index_dashbord_data',
        'schedule': crontab(), 
        # 'args': ('manager@company.com',),
    }
}