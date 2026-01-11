# 导入task模块
imports = ("src.core.celery.task.testcase_task", "src.core.celery.task.scheduled_task")
# 使用utc时区
enable_utc = False
# 时区
timezone = "Asia/Shanghai"
# started状态显示
task_track_started = True

# 根据运行平台和模式自动适配配置
import sys
import os

if 'beat' in sys.argv:
    # Beat 模式：启用自定义调度器（适用于所有平台）
    try:
        from .scheduler import DatabaseScheduler
        beat_scheduler = DatabaseScheduler
    except ImportError as e:
        print(f"导入自定义调度器失败: {e}")
else:
    # Worker 模式：根据平台选择合适的并发池
    if os.name == 'nt':  # Windows平台
        # Windows 上使用 spawn 方式创建进程，必须避免多进程 pickle 问题
        worker_pool = 'solo'
        worker_concurrency = 1
    else:  # Linux/macOS平台
        # Unix 平台可以使用多进程，充分利用多核CPU
        worker_pool = 'prefork'
        worker_concurrency = 4  # 根据CPU核心数调整
