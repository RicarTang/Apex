from celery.beat import Scheduler, ScheduleEntry
from celery.schedules import crontab, schedule, maybe_schedule
import time
from datetime import datetime, timedelta
import json
from src.utils.log_util import log
from src.config import config
from src.utils.sql_engine import engine
import pytz
from sqlalchemy import text
import copy
import heapq
import math

def is_numeric_value(value):
    return isinstance(value, (int, float))

class DatabaseScheduleEntry(ScheduleEntry):
    """数据库任务调度条目"""
    
    def __eq__(self, other):
        """重写 == 比较运算符，只比较关键信息，忽略 last_run_at、total_run_count 等动态变化字段"""
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
            last_run_at = db_task.last_run_at or datetime.now(pytz.utc)
            # 确保时间是UTC时区
            if last_run_at.tzinfo is None:
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
    
    # 移除动态计算的 next_run_at 属性，让 Celery 父类处理
    # @property
    # def next_run_at(self):
    #     """动态计算下次运行时间作为属性"""
    #     if hasattr(self, 'schedule') and hasattr(self, 'last_run_at'):
    #         is_due_result, next_time_seconds = self.schedule.is_due(self.last_run_at)
    #         return self.last_run_at + timedelta(seconds=next_time_seconds)
    #     return None
    
    def parse_cron_expression(self, cron_expr):
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
                        return schedule(timedelta(**{attr: value}))
            
            # 如果不是时间间隔格式，尝试解析为cron表达式
            parts = cron_expr.split()
            if len(parts) != 5:
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
        self.update_interval = kwargs.get('update_interval', 10.0)  # 每10秒检查一次数据库
        self.last_update_time = time.time()  # 记录最后更新时间
        
        super().__init__(app, *args, **kwargs)
        # 设置最大间隔（要在调用 super() 后设置，避免被父类覆盖）
        self.max_interval = kwargs.get('max_interval', 300.0)
        self.data = {}  # 清空默认任务，使用数据库任务
        
        # 从数据库加载并启用任务
        self.update_from_database()
        
        log.info(f"DatabaseScheduler调度器初始化成功，加载了 {len(self.schedule)} 个任务")
        log.info(f"已加载任务列表: {list(self.schedule.keys())}")
        log.info(f"max_interval 设置为 {self.max_interval}")
    
    
    def schedules_equal(self, old_schedules: dict, new_schedules: dict):
        """重写父类方法，确保仅在任务定义真正变化时才返回false!"""
        log.info(f"schedules_equal开始执行! old: {old_schedules}, new: {new_schedules}")
        if old_schedules is new_schedules is None:
            log.info("两个对象都是空的，返回True")
            return True
        if old_schedules is None or new_schedules is None:
            log.info("有一个是空的，返回False")
            return False
        old_keys = set(old_schedules.keys())
        new_keys = set(new_schedules.keys())
        log.info(f"old_keys: {old_keys}, new_keys: {new_keys}")
        if old_keys != new_keys:
            log.info("任务名称有差异，返回False")
            return False
        for name, old_entry in old_schedules.items():
            new_entry = new_schedules.get(name)
            log.info(f"开始比对任务 entry: {name}")
            if not new_entry:
                log.info("新任务中没有该任务，返回False")
                return False
            log.info(f"old_entry: {old_entry}")
            log.info(f"new_entry: {new_entry}")
            
            # 比较任务的关键字段，忽略 last_run_at 和 total_run_count 等动态字段
            are_equal = (
                old_entry.task == new_entry.task and
                old_entry.args == new_entry.args and
                old_entry.kwargs == new_entry.kwargs and
                str(old_entry.schedule) == str(new_entry.schedule)
            )
            log.info(f"关键字段是否相等: {are_equal}")
            
            if not are_equal:
                log.info("任务字段有差异，返回False")
                return False
        log.info("所有任务字段都相等，返回True")
        return True
    
    def update_from_database(self):
        """从数据库加载所有已启用的周期性任务到调度器，但只有当任务真正变化时才更新"""
        log.info("开始从数据库获取所有已启用的周期性任务")
        
        try:
            tasks = self._get_enabled_tasks()
            
            # 检查任务数量或关键字段是否变化
            # 如果没有变化，直接返回不更新
            if len(self.data) == len(tasks):
                same = True
                for task in tasks:
                    if task.name not in self.data:
                        same = False
                        break
                    old_entry = self.data[task.name]
                    # 比较关键字段
                    schedule = self.Entry.parse_cron_expression(None, task.cron_expression)  # 使用静态方法解析
                    if (old_entry.task != task.task or
                        str(old_entry.schedule) != str(schedule) or
                        old_entry.args != json.loads(task.task_args) if task.task_args else () or
                        old_entry.kwargs != json.loads(task.task_kwargs) if task.task_kwargs else {}):
                        same = False
                        break
                if same:
                    log.info("数据库任务没有变化，跳过更新")
                    return 
            
            # 仅在检测到更改时更新（例如新任务、删除任务或任务配置更改）
            new_schedule = {}
            log.debug(f"从数据库查询到 {len(tasks)} 个已启用任务")
            
            for task in tasks:
                log.debug(f"处理任务: {task.name}, cron: {task.cron_expression}")
                try:
                    import pytz
                    # 检查任务是否已经存在于当前 schedule 中
                    if task.name in self.data:
                        log.info(f"任务 {task.name} 已存在于调度器中 - 保持内存中的 last_run_at")
                        # 如果任务已经存在，使用内存中的 last_run_at 和 total_run_count
                        existing_entry = self.data[task.name]
                        # 更新 db_task 的 last_run_at 为内存中的值
                        task.last_run_at = existing_entry.last_run_at
                        task.total_run_count = existing_entry.total_run_count
                        log.debug(f"使用内存中的 last_run_at: {task.last_run_at}")
                    else:
                        # 新任务 - 设置默认 last_run_at
                        if task.last_run_at is None:
                            current_time = datetime.now(tz=pytz.utc)
                            reasonable_last_run = current_time - timedelta(minutes=1)
                            log.info(f"为新任务 {task.name} 设置默认 last_run_at: {reasonable_last_run}")
                            task.last_run_at = reasonable_last_run
                    # 确保时间是 UTC
                    if task.last_run_at and task.last_run_at.tzinfo is None:
                        task.last_run_at = pytz.utc.localize(task.last_run_at)
                    
                    entry = DatabaseScheduleEntry(app=self.app, db_task=task)
                    new_schedule[task.name] = entry
                    log.info(f"添加任务到调度器: {task.name}")
                except Exception as e:
                    log.error(f"创建任务 {task.name} 的调度条目时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            self.data = new_schedule
            self._heap = None
            self.old_schedulers = None
            DatabaseScheduler._global_schedule = new_schedule
            log.info(f"成功从数据库加载 {len(new_schedule)} 个已启用任务")
            
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
    
    def tick(self, event_t=None, min=min, heappop=heapq.heappop, heappush=heapq.heappush):
        """重写父类 tick 方法，确保任务能按数据库配置正确执行
        
        主要修复：
        1. 处理所有同时到期的任务，避免任务被忽略
        2. 正确处理任务到期检查和执行
        3. 防止重复执行
        4. 同步任务状态到数据库
        """
        from celery.beat import event_t as celery_event_t
        if event_t is None:
            event_t = celery_event_t
        
        current_time = time.time()
        
        # 设置合理的最大间隔，保证调度精度
        self.max_interval = 5.0
        
        # 周期性检查并更新数据库
        if current_time - self.last_update_time >= self.update_interval:
            log.info('检查数据库任务配置更新...')
            self.update_from_database()
            self.last_update_time = current_time

        # 重新填充堆如果调度有变化
        if self._heap is None or not self.schedules_equal(self.old_schedulers, self.schedule):
            self.old_schedulers = copy.copy(self.schedule)
            self.populate_heap()

        H = self._heap
        if not H:
            return self.max_interval

        # 处理所有到期任务
        while H:
            event = H[0]
            entry = event[2]

            # 检查任务是否到期
            is_due, next_time_to_run = entry.schedule.is_due(entry.last_run_at)

            if is_due:
                log.info(f'执行任务: {entry.name}, 间隔: {entry.schedule}')

                # 从堆中弹出任务
                verify = heappop(H)
                if verify is event:
                    # 使用父类方法正确处理任务预留
                    entry = self.reserve(entry)

                    # 执行任务
                    self.apply_entry(entry, producer=self.producer)

                    # 同步任务状态到数据库
                    self.sync(task_name=entry.name)

                    # 计算下一次运行时间并压入堆
                    heappush(H, event_t(self._when(entry, next_time_to_run), event[1], entry))

                    log.info(f'任务 {entry.name} 执行完成，下次运行间隔: {next_time_to_run} 秒')
                else:
                    heappush(H, verify)
            else:
                break  # 没有更多到期任务

        # 计算下一次 tick 的间隔
        next_interval = self.max_interval
        if H:
            next_entry = H[0][2]
            is_due_next, next_time = next_entry.schedule.is_due(next_entry.last_run_at)
            if is_numeric_value(next_time):
                next_interval = min(next_time, self.max_interval)

        return next_interval

    def reserve(self, entry):
        """正确预留任务下一次运行时间，防止重复执行"""
        from datetime import datetime
        import pytz
        
        # 手动更新 last_run_at 为当前 UTC 时间
        current_utc_time = datetime.now(pytz.utc)
        entry.last_run_at = current_utc_time
        entry.total_run_count += 1
        
        log.debug(f"任务: {entry.name} 已预留，上次运行: {entry.last_run_at}, 运行次数: {entry.total_run_count}")
        return entry

    @property
    def entries(self):
        """返回所有任务条目"""
        return self.schedule
    
    
    
    def _update_task_in_db(self, entry):
        """更新单个任务状态到数据库"""
        try:
            self._sync_update_task_in_db(entry)
        except Exception as e:
            log.error(f"同步任务: {entry.name} 到数据库失败: {str(e)}")

    def _sync_update_task_in_db(self, entry):
        """同步更新单个任务状态到数据库"""
        try:
            with engine.connect() as con:
                # 计算下次运行时间
                is_due, next_time_seconds = entry.schedule.is_due(entry.last_run_at)
                next_run_at = entry.last_run_at + timedelta(seconds=next_time_seconds)
                
                update_query = text("""
                    UPDATE scheduled_task
                    SET last_run_at = :last_run_at, next_run_at = :next_run_at, total_run_count = :total_run_count
                    WHERE name = :name
                """)
                
                # 使用命名参数执行更新
                con.execute(
                    update_query,
                    {
                        "last_run_at": entry.last_run_at,
                        "next_run_at": next_run_at,
                        "total_run_count": entry.total_run_count,
                        "name": entry.name
                    }
                )
                con.commit()
                
                log.info(f"任务: {entry.name}，数据库状态更新成功")
            
        except Exception as e:
            log.error(f"数据库更新任务: {entry.name} 失败: {str(e)}")
    
    def close(self):
        """关闭调度器，确保所有待同步任务都被同步，并且只执行一次"""
        if hasattr(self, '_closed') and self._closed:
            return  # 避免重复关闭和重复同步
        log.info("关闭beat执行close")
        # log.info("执行close，处理待关闭的连接和剩余同步任务")
        
        # # 同步所有待更新任务到数据库
        # if self.pending_updates:
        #     log.info(f"关闭时同步剩余 {len(self.pending_updates)} 个待更新任务")
        #     self.sync(pending_only=True)
        #     self.pending_updates.clear()
        
        self._closed = True  # 标记已关闭
        super().close()

    def sync(self, task_name=None, pending_only=False):
        """同步任务状态到数据库
        
        参数:
            task_name (str): 可选参数，指定要同步的单个任务名称
            pending_only (bool): 仅同步待更新集合中的任务
            如果未指定任何参数，默认同步所有任务
        """
        log.info('开始同步任务状态到数据库...')
        try:
            if pending_only:
                # 只同步待更新集合中的任务
                log.info(f'同步待更新任务: {list(self.pending_updates)}')
                for task_name in self.pending_updates:
                    if task_name in self.schedule:
                        entry = self.schedule[task_name]
                        self._update_task_in_db(entry)
                    else:
                        log.warning(f'任务 {task_name} 不在调度器中，跳过同步')
                log.info(f'{len(self.pending_updates)} 个待更新任务同步完成')
            elif task_name:
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
    
    def trigger_update(self):
        """手动触发从数据库更新任务列表
        可以通过 API 调用此方法，在动态添加/修改任务后立即更新
        """
        log.info("Manual task update triggered")
        self.update_from_database()
        self.last_update_time = time.time()
        DatabaseScheduler._last_update_time = self.last_update_time
        log.info(f"Updated {len(self.schedule)} tasks after manual trigger")