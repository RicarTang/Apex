# src/core/celery/scheduler.py
from celery.beat import Scheduler
import heapq
import time
import json
from datetime import datetime, timedelta
from celery.schedules import crontab
from sqlalchemy import text
from src.utils.sql_engine import engine
from src.utils.log_util import log
import threading


class TaskEntry:
    """任务条目"""

    __slots__ = (
        "name",
        "task",
        "schedule",
        "last_run",
        "next_run",
        "args",
        "kwargs",
        "options",
    )

    def __init__(self, name, task, schedule, args=(), kwargs={}, options={}):
        self.name = name
        self.task = task
        self.schedule = schedule
        self.args = args
        self.kwargs = kwargs
        self.options = options
        self.last_run = None
        self.next_run = self.calculate_next_run()
        log.debug(f"创建任务条目: {name}, 下次执行: {self.next_run}")

    def calculate_next_run(self):
        """计算下次执行时间"""
        due, next_time = self.schedule.is_due(self.last_run)
        if next_time is None:
            return datetime.now()
        return datetime.now() + timedelta(seconds=next_time)

    def is_due(self):
        """检查是否到期"""
        return datetime.now() >= self.next_run

    def mark_executed(self):
        """标记已执行"""
        self.last_run = datetime.now()
        self.next_run = self.calculate_next_run()
        log.debug(f"任务 {self.name} 已执行, 下次执行: {self.next_run}")

    def __lt__(self, other):
        return self.next_run < other.next_run


class StableScheduler(Scheduler):
    """稳定可靠的动态任务调度器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialized = False
        self.task_heap = []  # 任务堆
        self.task_map = {}  # 任务映射
        self.max_interval = 30  # 最大检查间隔
        self.last_update = time.time()
        self.update_interval = 300  # 5分钟更新一次任务
        self._lock = threading.Lock()

        # 确保只初始化一次
        if not self._initialized:
            self.setup()
            self._initialized = True

    def setup(self):
        """初始化方法，Beat启动时调用"""
        log.info("=" * 50)
        log.info("初始化调度器")

        # 从数据库加载任务
        self.update_tasks()

        log.info(f"已加载 {len(self.task_heap)} 个任务")
        log.info("=" * 50)

    def update_tasks(self):
        """从数据库更新任务配置"""
        log.info("更新任务配置")
        try:
            # 保存当前任务状态
            current_state = {}
            for entry in self.task_heap:
                current_state[entry.name] = {
                    "last_run": entry.last_run,
                    "next_run": entry.next_run,
                }
            log.debug(f"保存了 {len(current_state)} 个任务状态")

            # 清空任务堆
            self.task_heap = []
            self.task_map = {}

            # 从数据库加载任务
            sql = text("SELECT * FROM scheduled_task WHERE status = 1")
            with engine.connect() as conn:
                tasks = conn.execute(sql).fetchall()
            log.info(f"从数据库获取到 {len(tasks)} 个任务")

            # 创建新任务条目
            for task in tasks:
                try:
                    cron_parts = task.cron_expression.split()

                    # 恢复任务状态（如果存在）
                    task_state = current_state.get(task.name, {})

                    # 创建任务条目
                    entry = TaskEntry(
                        name=task.name,
                        task=task.task,
                        schedule=crontab(
                            minute=cron_parts[0],
                            hour=cron_parts[1],
                            day_of_month=cron_parts[2],
                            month_of_year=cron_parts[3],
                            day_of_week=cron_parts[4],
                        ),
                        kwargs=(
                            json.loads(task.task_kwargs) if task.task_kwargs else {}
                        ),
                    )

                    # 恢复状态
                    if task_state:
                        entry.last_run = task_state.get("last_run")
                        entry.next_run = task_state.get(
                            "next_run", entry.calculate_next_run()
                        )

                    # 添加到堆和映射
                    heapq.heappush(self.task_heap, entry)
                    self.task_map[task.name] = entry
                    log.info(f"添加任务: {task.name}")
                except Exception as e:
                    log.error(f"添加任务 {task.name} 失败: {str(e)}", exc_info=True)

            log.info(f"成功更新 {len(self.task_heap)} 个任务")
        except Exception as e:
            log.error(f"更新任务失败: {str(e)}", exc_info=True)

    def tick(self):
        """核心调度方法"""
        try:
            # 检查任务更新
            current_time = time.time()
            if current_time - self.last_update > self.update_interval:
                self.update_tasks()
                self.last_update = current_time

            # 处理到期任务
            self.process_due_tasks()

            # 计算下次唤醒时间
            return self.calculate_next_interval()
        except Exception as e:
            log.error(f"tick() 方法执行失败: {str(e)}", exc_info=True)
            return self.max_interval

    def process_due_tasks(self):
        """处理所有到期任务"""
        now = datetime.now()
        executed = 0
        processed_entries = []

        while self.task_heap and self.task_heap[0].is_due():
            task = heapq.heappop(self.task_heap)

            try:
                # 发送任务
                self.apply_async(
                    task.task, args=task.args, kwargs=task.kwargs, **task.options
                )
                log.info(f"发送任务: {task.name}")
                executed += 1

                # 更新任务状态
                task.mark_executed()
            except Exception as e:
                log.error(f"发送任务失败: {str(e)}", exc_info=True)

            # 添加到处理列表
            processed_entries.append(task)

        # 将处理过的任务重新加入堆
        for task in processed_entries:
            heapq.heappush(self.task_heap, task)

        if executed:
            log.info(f"本次执行了 {executed} 个任务")

    def calculate_next_interval(self):
        """计算下次唤醒时间"""
        if not self.task_heap:
            return self.max_interval

        next_task = self.task_heap[0]
        now = datetime.now()
        wait_seconds = (next_task.next_run - now).total_seconds()

        # 确保在合理范围内
        if wait_seconds < 0:
            return 0.1
        if wait_seconds > self.max_interval:
            return self.max_interval

        return wait_seconds
