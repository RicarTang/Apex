import json
import time
import heapq
from datetime import datetime, timedelta
import pytz
from sqlalchemy import text
from collections import namedtuple
from typing import Union
from celery.beat import Scheduler, ScheduleEntry
from celery.schedules import crontab, schedule
from src.utils.log_util import log
from src.config import config
from src.utils.sql_engine import engine



# 定义事件类型，用于调度堆
event_t = namedtuple('event_t', ('time', 'priority', 'entry'))

def is_numeric_value(value):
    return isinstance(value, (int, float))

class DatabaseScheduleEntry(ScheduleEntry):
    """数据库任务调度条目"""
    
    def __eq__(self, other):
        """重写 == 比较运算符，只比较关键信息，忽略 options"""
        if not isinstance(other, DatabaseScheduleEntry):
            return NotImplemented
        # 比较关键字段
        return (
            self.task == other.task and
            str(self.schedule) == str(other.schedule) and
            self.args == other.args and
            self.kwargs == other.kwargs and
            self.name == other.name
        )
    
    def __init__(self, app=None, db_task=None, **kwargs):
        """构造函数，支持从数据库模型或关键字参数创建任务条目"""
        if db_task:
            # 从数据库模型创建
            schedule = self.parse_cron_expression(db_task.cron_expression)
            last_run_at = db_task.last_run_at
            
            # 正确设置默认 last_run_at
            if not last_run_at:
                current_time = datetime.now(pytz.utc)
                # 对于新任务，设置一个合理的过去时间，以便任务能立即执行
                last_run_at = current_time - timedelta(minutes=1)
                log.debug(f"任务 {db_task.name} 设置默认 last_run_at: {last_run_at}")
            else:
                # 确保时间是 UTC 时区
                if last_run_at.tzinfo is None or last_run_at.tzinfo.utcoffset(last_run_at) is None:
                    last_run_at = pytz.utc.localize(last_run_at)
                else:
                    last_run_at = last_run_at.astimezone(pytz.utc)
            
            kwargs = {
                'name': db_task.name,
                'task': db_task.task,
                'schedule': schedule,
                'args': json.loads(db_task.task_args) if db_task.task_args else (),
                'kwargs': json.loads(db_task.task_kwargs) if db_task.task_kwargs else {},
                'last_run_at': last_run_at,
                'total_run_count': db_task.total_run_count or 0,
                'app': app
            }
            
            # 调用父类构造函数
            super().__init__(**kwargs)
            
            self.db_task = db_task
            self.status = db_task.status
            self.schedule = schedule
        else:
            # 从关键字参数创建（与Celery原生兼容）
            super().__init__(**kwargs)
            self.db_task = None
        
    
    def __next__(self):
        """生成下一个任务调度条目"""
        next_entry = self.__class__(
            name=self.name,
            task=self.task,
            schedule=self.schedule,
            args=self.args,
            kwargs=self.kwargs,
            last_run_at=self.last_run_at,
            total_run_count=self.total_run_count,
            app=self.app
        )
        
        # 手动更新 last_run_at 为当前 UTC 时间
        current_utc_time = datetime.now(pytz.utc)
        next_entry.last_run_at = current_utc_time
        next_entry.total_run_count += 1
        
        # 计算下次运行时间
        is_due, next_time_to_run = next_entry.schedule.is_due(next_entry.last_run_at)
        next_entry.next_run_at = next_entry.last_run_at + timedelta(seconds=next_time_to_run)
        
        return next_entry
    
    
    def parse_cron_expression(self, cron_expr: str) -> Union[crontab, schedule]:
        """解析cron表达式或时间间隔
        
        支持格式：
        - Cron 表达式: 例如 "0 * * * *" (每小时执行)
        - 时间间隔: 例如 "10s"(10秒), "1m"(1分钟), "1h"(1小时), "1d"(1天), "5"(5秒)"
        """
        try:
            # 先尝试解析为时间间隔
            interval_str = cron_expr.strip()
            
            # 纯数字格式
            if interval_str.isdigit():
                seconds = int(interval_str)
                return schedule(timedelta(seconds=seconds))
            
            # 带单位格式
            units = {
                's': 'seconds',
                'm': 'minutes',
                'h': 'hours',
                'd': 'days'
            }
            
            for unit, attr in units.items():
                if interval_str.endswith(unit):
                    value_str = interval_str[:-1].strip()
                    if value_str.isdigit():
                        value = int(value_str)
                        sched = schedule(timedelta(**{attr: value}))
                        
                        # 测试 is_due 方法的行为
                        current_time = datetime.now(pytz.utc)
                        last_run = current_time - timedelta(seconds=5)  # 假设5秒前运行
                        is_due, next_time = sched.is_due(last_run)
                        
                        return sched
            
            # 如果不是时间间隔格式，尝试解析为cron表达式
            parts = cron_expr.split()
            if len(parts) != 5:
                log.error(f"无效的cron表达式: {cron_expr}")
                raise ValueError(f"无效的cron表达式: {cron_expr}")
                
            minute, hour, day_of_month, month_of_year, day_of_week = parts
            return crontab(minute=minute, hour=hour, day_of_month=day_of_month,
                          month_of_year=month_of_year, day_of_week=day_of_week)
        except Exception as e:
            log.error(f"解析任务调度表达式 {cron_expr} 失败: {str(e)}")
            raise

class DatabaseScheduler(Scheduler):
    """基于数据库的Celery周期性任务调度器，继承自Celery内置的周期性任务调度器"""
    Entry = DatabaseScheduleEntry
    
    def __init__(self, app, *args, **kwargs):
        """初始化方法"""
        log.info("开始初始化自定义调度器DatabaseScheduler")
        self.update_interval = kwargs.get('update_interval', config.CELERY_BEAT_UPDATE_INTERVAL)  # 检查数据库任务的间隔时间
        self.last_update_time = time.time()  # 记录最后更新时间
        
        super().__init__(app, *args, **kwargs)
        self.max_interval = config.CELERY_BEAT_MAX_INTERVAL
        self.data = {}  # 清空默认任务，使用数据库任务
        
        # 从数据库加载并启用任务
        self.update_from_database()
        
        log.info(f"DatabaseScheduler调度器初始化成功，加载了 {len(self.schedule)} 个任务")
        log.info(f"已加载任务列表: {list(self.schedule.keys())}")
        log.info(f"max_interval 设置为 {self.max_interval}")
    
    

    
    def update_from_database(self):
        """从数据库加载所有已启用的周期性任务到调度器，确保每次都正确更新任务列表"""
        try:
            tasks = self._get_enabled_tasks()
            log.debug(f"从数据库查询到 {len(tasks)} 个已启用任务")
            # 初始化新的任务调度字典
            new_schedule = {}
            
            for task in tasks:
                try:
                    # 首先确保任务时间是 UTC 时区的 aware 时间
                    if task.last_run_at and (task.last_run_at.tzinfo is None or task.last_run_at.tzinfo.utcoffset(task.last_run_at) is None):
                        task.last_run_at = pytz.utc.localize(task.last_run_at)
                    elif task.last_run_at:
                        task.last_run_at = task.last_run_at.astimezone(pytz.utc)
                    
                    # 检查任务是否已经存在于当前 schedule 中
                    if task.name in self.data:
                        
                        # 如果任务已经存在，使用内存中的 last_run_at 和 total_run_count
                        existing_entry = self.data[task.name]
                        # 更新 db_task 的 last_run_at 为内存中的值
                        task.last_run_at = existing_entry.last_run_at
                        task.total_run_count = existing_entry.total_run_count
                    else:
                        # 新任务 - 设置默认 last_run_at
                        log.info(f"添加任务到调度器: {task.name}")
                        if task.last_run_at is None:
                            current_time = datetime.now(tz=pytz.utc)
                            reasonable_last_run = current_time - timedelta(minutes=1)
                            log.info(f"为新任务 {task.name} 设置默认 last_run_at: {reasonable_last_run}")
                            task.last_run_at = reasonable_last_run
                        else:
                            # 检查 last_run_at 是否在未来时间（可能是数据库存储错误）
                            current_time = datetime.now(tz=pytz.utc)
                            log.debug(f"任务 {task.name} 从数据库读取到 last_run_at: {task.last_run_at}，当前时间: {current_time}")
                            # 计算时间差
                            time_diff = current_time - task.last_run_at
                            log.debug(f"任务 {task.name} 时间差: {time_diff.total_seconds()} 秒")
                            
                            # 如果 last_run_at 在未来时间，重置为合理的过去时间
                            if time_diff.total_seconds() < 0:
                                log.warning(f"任务 {task.name} last_run_at 在未来时间，调整为合理的过去时间")
                                reasonable_last_run = current_time - timedelta(minutes=1)
                                task.last_run_at = reasonable_last_run
                            else:
                                # 如果任务从数据库读取到了 last_run_at，但间隔太短，需要调整
                                # 解析任务调度间隔
                                task_schedule = self.Entry.parse_cron_expression(None, task.cron_expression)
                                if hasattr(task_schedule, 'seconds'):
                                    interval = task_schedule.seconds
                                    log.debug(f"任务 {task.name} 调度间隔: {interval} 秒")
                                    # 如果任务的 last_run_at 太近（小于间隔），调整到合理的过去时间
                                    if time_diff.total_seconds() < interval:
                                        adjusted_last_run = current_time - timedelta(seconds=interval * 2)
                                        log.warning(f"任务 {task.name} last_run_at 太近，调整为: {adjusted_last_run}")
                                        task.last_run_at = adjusted_last_run

                        
                    entry = DatabaseScheduleEntry(app=self.app, db_task=task)
                    new_schedule[task.name] = entry
                except Exception as e:
                    log.error(f"创建任务 {task.name} 的调度条目时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            self.data = new_schedule
            self._heap = None
            self.old_schedulers = None
            DatabaseScheduler._global_schedule = new_schedule
            
        except Exception as e:
            log.error(f"从数据库更新任务调度器时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_enabled_tasks(self):
        """同步获取启用的任务"""
        query = text("""
                SELECT id, name, task, cron_expression, task_args, task_kwargs,
                       last_run_at, next_run_at, total_run_count, status, is_delete
                FROM scheduled_task
                WHERE is_delete = 0 AND status = 1
            """)
        try:
            with engine.connect() as con:
                result = con.execute(query)
                rows = result.fetchall()
                
            # 将 SQLAlchemy Row 对象转换为可访问的对象
            class TaskObject:
                def __init__(self, row):
                    # 按查询顺序获取字段值
                    self.id = row[0]
                    self.name = row[1]
                    self.task = row[2]
                    self.cron_expression = row[3]
                    self.task_args = row[4]
                    self.task_kwargs = row[5]
                    self.last_run_at = row[6] if isinstance(row[6], datetime) else (datetime.strptime(row[6], '%Y-%m-%d %H:%M:%S') if row[6] else None)
                    self.next_run_at = row[7] if isinstance(row[7], datetime) else (datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S') if row[7] else None)
                    self.total_run_count = row[8] or 0
                    self.status = row[9]
                    self.is_delete = row[10]
            
            return [TaskObject(row) for row in rows]
            
        except Exception as e:
            log.error(f"数据库查询失败: {str(e)}")
            return []
    
 
        
    def tick(self, event_t = None, min=min, heappop=heapq.heappop, heappush=heapq.heappush):
        """beat核心功能，添加数据库同步功能
        """
        from celery.beat import event_t as celery_event_t
        if event_t is None:
            event_t = celery_event_t
        
        current_time = time.time()
        # 周期性检查并更新数据库
        if current_time - self.last_update_time >= self.update_interval:
            log.debug('检查数据库任务配置更新...')
            self.update_from_database()
            self.last_update_time = current_time
        super().tick(event_t, min, heappop, heappush)
    
    def _update_task_in_db(self, entry: ScheduleEntry) -> None:
        """更新单个任务状态到数据库"""
        try:
            self._sync_update_task_in_db(entry)
        except Exception as e:
            log.error(f"同步任务: {entry.name} 到数据库失败: {str(e)}")

    def _sync_update_task_in_db(self, entry: ScheduleEntry) -> None:
        """同步更新单个任务状态到数据库"""
        try:
            with engine.connect() as con:
                # 计算下次运行时间
                is_due, next_time_seconds = entry.schedule.is_due(entry.last_run_at)
                next_run_at = entry.last_run_at + timedelta(seconds=next_time_seconds)
                
                log.debug(f"任务: {entry.name}，上次运行: {entry.last_run_at}, 下次运行: {next_run_at}, 间隔: {next_time_seconds}秒")
                
                update_query = text("""
                    UPDATE scheduled_task
                    SET last_run_at = :last_run_at, next_run_at = :next_run_at, total_run_count = :total_run_count
                    WHERE name = :name
                """)
                
                # 确保时间是 UTC 时区
                last_run_at_utc = entry.last_run_at
                if last_run_at_utc.tzinfo is None or last_run_at_utc.tzinfo.utcoffset(last_run_at_utc) is None:
                    last_run_at_utc = pytz.utc.localize(last_run_at_utc)
                else:
                    last_run_at_utc = last_run_at_utc.astimezone(pytz.utc)
                
                next_run_at_utc = next_run_at
                if next_run_at_utc.tzinfo is None or next_run_at_utc.tzinfo.utcoffset(next_run_at_utc) is None:
                    next_run_at_utc = pytz.utc.localize(next_run_at_utc)
                else:
                    next_run_at_utc = next_run_at_utc.astimezone(pytz.utc)
                
                # 使用命名参数执行更新
                con.execute(
                    update_query,
                    {
                        "last_run_at": last_run_at_utc,
                        "next_run_at": next_run_at_utc,
                        "total_run_count": entry.total_run_count,
                        "name": entry.name
                    }
                )
                con.commit()
                
                log.info(f"任务: {entry.name}，数据库状态更新成功")
            
        except Exception as e:
            log.error(f"数据库更新任务: {entry.name} 失败: {str(e)}")
    

    def sync(self, task_name: str = None) -> None:
        """同步任务状态到数据库
        
        参数:
            task_name (str): 可选参数，指定要同步的单个任务名称
            如果未指定任何参数，默认同步所有任务
        """
        log.info('开始同步任务状态到数据库...')
        try:
            if task_name:
                # 只同步指定的单个任务
                if task_name in self.schedule:
                    entry = self.schedule[task_name]
                    self._update_task_in_db(entry)
                    log.info(f'单个任务 {task_name} 状态同步完成')
                else:
                    log.warning(f'任务 {task_name} 不在调度器中，跳过同步')
            else:
                # 同步所有任务
                for name, entry in self.schedule.items():
                    self._update_task_in_db(entry)
                log.info('所有任务状态同步完成')
        except Exception as e:
            log.error(f'同步任务状态到数据库时出错: {e}', exc_info=True)
