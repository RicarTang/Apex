"""测试环境schmea"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from fastapi import status, HTTPException
from ..common import PageParam, CommonMixinModel
from src.utils.enum_util import BoolEnum
from croniter import croniter, CroniterBadCronError


class TaskMixinModel(BaseModel):
    """task Mixin"""

    name: str = Field(min_length=3, max_length=30, description="任务唯一标识")
    task: str = Field(min_length=10, max_length=100, description="任务路径")
    cron_expression: str = Field(
        max_length=30, alias="cronExpression", description="任务cron表达式"
    )
    task_kwargs: Optional[dict] = Field(
        default=None, alias="taskKwargs", description="任务参数，json类型"
    )
    status: Optional[BoolEnum] = Field(default=BoolEnum.TRUE, description="任务状态")
    remark: Optional[str] = Field(default=None, max_length=100, description="备注")

    @field_validator("cron_expression")
    @classmethod
    def cron_expression_validate(cls, v: str):
        """校验cron表达式

        Args:
            v (str): _description_

        Returns:
            str: _description_
        """
        try:
            croniter(v, datetime.now())
            return v
        except CroniterBadCronError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"无效的 Cron 表达式:{str(exc)}",
            )


class TaskIn(TaskMixinModel):
    """task req schema"""


class TaskOut(CommonMixinModel, TaskMixinModel):
    """task res schema"""

    cron_expression: str = Field(
        max_length=30,
        serialization_alias="cronExpression",
        description="任务cron表达式",
    )


class TaskListOut(PageParam):
    """task res list schema"""

    data: List[TaskOut]
