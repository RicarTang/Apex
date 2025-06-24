"""task数据访问模块"""

from src.repositories import BaseRepository
from src.db.models import ScheduledTask


class TaskRepository(BaseRepository[ScheduledTask]):
    """任务数据访问仓库

    Args:
        BaseRepository (_type_): _description_
    """

    model = ScheduledTask
