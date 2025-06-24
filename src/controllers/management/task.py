"""定时任务路由"""

from typing import Optional
from fastapi import APIRouter, Query, Path
from src.schemas.management.task import (
    TaskIn,
    TaskOut,
    TaskListOut,
)
from src.schemas import ResultResponse
from src.services import TaskService


router = APIRouter()


@router.get(
    "/list",
    summary="任务列表",
    response_model=ResultResponse[TaskListOut],
)
async def get_task_list(
    task_name: Optional[str] = Query(
        default=None,
        description="任务标识",
        alias="taskName",
    ),
    task_status: Optional[int] = Query(
        default=None, description="任务状态", alias="status"
    ),
    begin_time: Optional[str] = Query(
        default=None,
        description="开始时间",
        alias="beginTime",
    ),
    end_time: Optional[str] = Query(
        default=None,
        description="结束时间",
        alias="endTime",
    ),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取task列表"""
    result, total = await TaskService.query_task_list(
        task_name=task_name,
        task_status=task_status,
        begin_time=begin_time,
        end_time=end_time,
        limit=limit,
        page=page,
    )
    return ResultResponse[TaskListOut](
        result=TaskListOut(data=result, page=page, limit=limit, total=total)
    )


@router.post(
    "/add",
    summary="创建task",
    response_model=ResultResponse[TaskOut],
    # dependencies=[Depends(Authority("user", "add"))],
)
async def create_task(body: TaskIn):
    """创建task."""
    task = await TaskService.create_task(body=body)
    return ResultResponse[TaskOut](result=task)


@router.get(
    "/{task_id}",
    summary="获取任务详情",
)
async def get_task_detail(task_id: int):
    """获取任务详情"""
    task = await TaskService.query_task_by_id(task_id=task_id)
    return ResultResponse[TaskOut](result=task)


# @router.delete(
#     "/{user_ids}",
#     response_model=ResultResponse[None],
#     summary="删除用户",
#     dependencies=[Depends(Authority("user", "delete"))],
# )
# async def delete_user(
#     user_ids: Annotated[
#         str, StringConstraints(strip_whitespace=True, pattern=r"^\d+(,\d+)*$")
#     ],
# ):
#     """删除用户."""
#     log.debug(user_ids)
#     # 解析User ids 为列表
#     source_ids_list = user_ids.split(",")
#     # 删除
#     await UserService.delete_user_from_id(source_ids_list)
#     return ResultResponse[None](message="successful deleted user!")


# @router.get(
#     "/{user_id}",
#     response_model=ResultResponse[UserOut],
#     summary="根据id查询用户",
#     dependencies=[Depends(Authority("user", "query"))],
# )
# async def get_user(user_id: int = Path(alias="")):
#     """根据id查询用户."""
#     q_user = await UserService.query_user_by_id(user_id)
#     return ResultResponse[UserOut](result=q_user)


# @router.put(
#     "/{user_id}",
#     response_model=ResultResponse[None],
#     summary="更新用户",
#     dependencies=[Depends(Authority("user", "update"))],
# )
# async def update_user(user_id: int, body: UserUpdateIn):
#     """更新用户信息."""
#     await UserService.update_user_from_id(user_id=user_id, body=body)
#     return ResultResponse[None](message="Update user information successfully!")
