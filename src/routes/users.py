from fastapi import APIRouter, HTTPException
from typing import List
from src.models import User_Pydantic, UserIn_Pydantic, Users
from tortoise.contrib.fastapi import HTTPNotFoundError
from .. import schemas
from passlib.hash import md5_crypt
from ..utils.log_util import log

user_route = APIRouter()


@user_route.get("/users",
                response_model=schemas.Users
                )
async def get_users():
    """获取所有用户."""
    result = await User_Pydantic.from_queryset(Users.all())
    return {"result": result}


@user_route.post("/users",
                 response_model=User_Pydantic
                 )
async def create_user(user: schemas.UserIn):
    """创建用户."""
    user.password = md5_crypt.hash(user.password)
    user_obj = await Users.create(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_tortoise_orm(user_obj)


@user_route.get(
    "/user/{user_id}",
    response_model=User_Pydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def get_user(user_id: int):
    """查询单个用户。"""
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@user_route.put(
    "/user/{user_id}",
    response_model=User_Pydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def update_user(user_id: int, user: UserIn_Pydantic):
    """更新用户信息。"""
    await Users.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@user_route.delete("/user/{user_id}",
                   response_model=schemas.Status,
                   responses={404: {"model": HTTPNotFoundError}}
                   )
async def delete_user(user_id: int):
    """删除用户。"""
    deleted_count = await Users.filter(id=user_id).delete()
    log.debug("")
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return schemas.Status(message=f"Deleted user {user_id}")
