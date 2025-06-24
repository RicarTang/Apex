"""Task业务逻辑层"""

from typing import Tuple, List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from src.db.models import ScheduledTask
from src.repositories.management.task import TaskRepository
from src.utils.log_util import log
from src.schemas.management.task import TaskIn
from src.utils.exceptions.task import TaskNotExistException


class TaskService:
    """task service层"""

    @classmethod
    async def query_task_list(
        cls,
        task_name: Optional[str],
        task_status: Optional[int],
        begin_time: Optional[str],
        end_time: Optional[str],
        limit: int,
        page: int,
    ) -> Tuple[List[ScheduledTask], int]:
        """查询任务列表

        Args:
            task_name (str): _description_
            task_status (int): _description_
            begin_time (str): _description_
            end_time (str): _description_
            limit (int): _description_
            page (int): _description_

        Returns:
            Tuple[List[Users], int]: _description_
        """
        # 筛选条件
        filters = {}
        if task_name:
            filters["name__icontains"] = task_name
        if task_status is not None:
            filters["status"] = task_status
        if begin_time:
            begin_time = datetime.strptime(begin_time, "%Y-%m-%d")
            filters["created_at__gte"] = begin_time
        if end_time:
            end_time = datetime.strptime(end_time, "%Y-%m-%d")
            filters["created_at__lte"] = end_time
        if begin_time and end_time:
            filters["created_at__range"] = (
                begin_time,
                end_time,
            )
        # 执行查询
        result, total = await TaskRepository.fetch_page_by_filter(
            limit=limit, page=page, **filters
        )
        return result, total

    @staticmethod
    async def query_task_by_id(task_id: int) -> ScheduledTask:
        """通过id查询task

        Args:
            id (int): id

        Raises:
            UserNotExistException: _description_
            HTTPException: _description_

        Returns:
            Users: _description_
        """
        try:
            query_result = await TaskRepository.fetch_by_pk(pk=task_id)
        except DoesNotExist as exc:
            raise TaskNotExistException from exc
        except MultipleObjectsReturned as exc:
            log.error("查询出多个同样的任务名称！")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Duplicate task name!",
            ) from exc
        else:
            return query_result

    @staticmethod
    async def create_task(body: TaskIn) -> ScheduledTask:
        """创建任务

        Args:
            body (TaskIn): 请求body

        Returns:
            ScheduledTask: _description_
        """
        task = await TaskRepository.create(**body.model_dump(exclude_unset=True))
        return task
