"""测试环境schmea"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from fastapi import status, HTTPException
from ..common import PageParam, CommonMixinModel
from src.utils.enum_util import BoolEnum
from croniter import croniter, CroniterBadCronError


def is_valid_time_interval(interval_str: str) -> bool:
    """验证时间间隔字符串是否有效
    
    支持格式：
    - 10s: 10秒
    - 1m: 1分钟
    - 1h: 1小时
    - 1d: 1天
    - 数字: 默认为秒
    """
    try:
        # 纯数字格式
        if interval_str.isdigit():
            return int(interval_str) > 0
        
        # 带单位格式
        interval_str = interval_str.strip()
        units = {
            's': 'seconds',
            'm': 'minutes',
            'h': 'hours',
            'd': 'days'
        }
        
        for unit in units:
            if interval_str.endswith(unit):
                value_str = interval_str[:-1].strip()
                if value_str.isdigit():
                    return int(value_str) > 0
        
        return False
    except:
        return False


class TaskMixinModel(BaseModel):
    """task Mixin"""

    name: str = Field(min_length=3, max_length=30, description="任务唯一标识")
    task: str = Field(min_length=10, max_length=100, description="任务路径")
    cron_expression: str = Field(
        max_length=30, alias="cronExpression", description="任务cron表达式或时间间隔(例如: 10s=10秒, 1m=1分钟)"
    )
    task_kwargs: Optional[dict] = Field(
        default=None, alias="taskKwargs", description="任务参数，json类型"
    )
    status: Optional[BoolEnum] = Field(default=BoolEnum.TRUE, description="任务状态")
    remark: Optional[str] = Field(default=None, max_length=100, description="备注")

    @field_validator("cron_expression")
    @classmethod
    def cron_expression_validate(cls, v: str):
        """校验cron表达式或时间间隔
        
        Args:
            v (str): _description_

        Returns:
            str: _description_
        """
        # 验证是否为有效的时间间隔
        if is_valid_time_interval(v):
            return v
            
        # 验证是否为有效的cron表达式
        try:
            croniter(v, datetime.now())
            return v
        except CroniterBadCronError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"无效的 Cron 表达式或时间间隔: {str(exc)}",
            )


class TaskIn(TaskMixinModel):
    """task req schema"""


class TaskOut(CommonMixinModel, TaskMixinModel):
    """task res schema"""

    cron_expression: str = Field(
        max_length=30,
        serialization_alias="cronExpression",
        description="任务cron表达式或时间间隔",
    )


class TaskListOut(PageParam):
    """task res list schema"""

    data: List[TaskOut]