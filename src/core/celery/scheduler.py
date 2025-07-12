# src/core/celery/simple_scheduler.py
from celery.beat import Scheduler
from celery.schedules import crontab
from sqlalchemy import text
from src.utils.sql_engine import engine
import time
from datetime import datetime, timedelta
import json
import heapq
from src.utils.log_util import log


class SimpleScheduleEntry:
    """简化任务条目"""

    __slots__ = ("name", "task", "schedule", "last_run", "next_run", "args", "kwargs")

    def __init__(
        self, name, task, schedule, last_run=None, next_run=None, args=(), kwargs={}
    ):
        self.name = name
        self.task = task
        self.schedule = schedule
        self.last_run = last_run
        self.next_run = next_run or self.calculate_next_run()
        self.args = args
        self.kwargs = kwargs

    def calculate_next_run(self):
        """计算下次执行时间"""
        due, next_time = self.schedule.is_due(self.last_run)
        return (
            datetime.now() + timedelta(seconds=next_time)
            if next_time
            else datetime.now()
        )

    def is_due(self):
        """检查是否到期"""
        return datetime.now() >= self.next_run

    def mark_executed(self):
        """标记已执行"""
        self.last_run = datetime.now()
        self.next_run = self.calculate_next_run()

    def __lt__(self, other):
        return self.next_run < other.next_run


class SimpleDatabaseScheduler(Scheduler):
    """简化数据库调度器"""

    def __init__(self, *args, **kwargs):
        # 提取 app 参数
        app = kwargs.get("app")
        if app is None and len(args) > 0:
            app = args[0]

        if app is None:
            raise ValueError("调度器需要 app 参数")

        # 调用父类构造函数
        super().__init__(app, *args, **kwargs)

        self.task_heap = []  # 任务堆
        self.max_interval = 30  # 最大检查间隔
        self.last_update = time.time()
        self.update_interval = 300  # 5分钟更新一次任务

        log.info("=" * 50)
        log.info("初始化简化调度器")
        self.update_tasks()
        log.info(f"已加载 {len(self.task_heap)} 个任务")
        log.info("=" * 50)

    def update_tasks(self):
        """从数据库更新任务配置"""
        log.info("更新任务配置")
        try:
            # 清空当前任务堆
            self.task_heap = []

            # 查询所有启用的任务
            sql = text("SELECT * FROM scheduled_tasks WHERE enabled = 1")
            with engine.connect() as session:
                tasks = session.execute(sql).fetchall()

            log.info(f"从数据库获取到 {len(tasks)} 个任务")

            # 创建任务条目
            for task in tasks:
                try:
                    cron_parts = task.cron_expression.split()

                    # 创建任务条目
                    entry = SimpleScheduleEntry(
                        name=task.name,
                        task=task.task,
                        schedule=crontab(
                            minute=cron_parts[0],
                            hour=cron_parts[1],
                            day_of_month=cron_parts[2],
                            month_of_year=cron_parts[3],
                            day_of_week=cron_parts[4],
                        ),
                        last_run=task.last_run_at,
                        next_run=task.next_run_at,
                        args=json.loads(task.task_args) if task.task_args else (),
                        kwargs=json.loads(task.task_kwargs) if task.task_kwargs else {},
                    )

                    # 添加到堆
                    heapq.heappush(self.task_heap, entry)
                    log.info(f"添加任务: {task.name}")
                except Exception as e:
                    log.error(f"添加任务 {task.name} 失败: {str(e)}")

            # # 添加测试任务
            # self.add_test_task()
        except Exception as e:
            log.error(f"更新任务失败: {str(e)}")

    # def add_test_task(self):
    #     """添加每分钟执行的测试任务"""
    #     try:
    #         entry = SimpleScheduleEntry(
    #             name="test_task",
    #             task="src.core.celery.task.test_task",
    #             schedule=crontab(minute="*"),
    #             args=("每分钟测试任务",),
    #         )
    #         heapq.heappush(self.task_heap, entry)
    #         log.info("已添加测试任务: test_task (每分钟执行)")
    #     except Exception as e:
    #         log.error(f"添加测试任务失败: {str(e)}")

    def tick(self):
        """核心调度方法"""
        # 检查任务更新
        current_time = time.time()
        if current_time - self.last_update > self.update_interval:
            self.update_tasks()
            self.last_update = current_time

        # 处理到期任务
        self.process_due_tasks()

        # 计算下次唤醒时间
        return self.calculate_next_interval()

    def process_due_tasks(self):
        """处理所有到期任务"""
        now = datetime.now()
        executed = 0
        processed_entries = []

        while self.task_heap and self.task_heap[0].is_due():
            task = heapq.heappop(self.task_heap)

            try:
                # 发送任务
                self.apply_async(task.task, args=task.args, kwargs=task.kwargs)
                log.info(f"发送任务: {task.name}")
                executed += 1

                # 更新任务状态
                task.mark_executed()

                # 更新数据库状态
                self.update_task_status(task)
            except Exception as e:
                log.error(f"发送任务失败: {str(e)}")

            # 添加到处理列表
            processed_entries.append(task)

        # 将处理过的任务重新加入堆
        for task in processed_entries:
            heapq.heappush(self.task_heap, task)

        if executed:
            log.info(f"本次执行了 {executed} 个任务")

    def update_task_status(self, task):
        """更新任务状态到数据库"""
        try:
            sql = text(
                """
                UPDATE scheduled_tasks 
                SET last_run_at = :last_run, 
                    next_run_at = :next_run,
                    total_run_count = total_run_count + 1
                WHERE name = :name
            """
            )

            with engine.connect() as session:
                session.execute(
                    sql,
                    {
                        "name": task.name,
                        "last_run": task.last_run,
                        "next_run": task.next_run,
                    },
                )
                session.commit()
                log.debug(f"更新任务状态: {task.name}")
        except Exception as e:
            log.error(f"更新任务状态失败: {str(e)}")

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

    def close(self):
        """关闭调度器"""
        super().close()
