from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from src.models import User_Pydantic, UserIn_Pydantic, Users
from tortoise.contrib.fastapi import HTTPNotFoundError
from .. import schemas
from ..utils.log_util import log
from ..utils import depends_util
from passlib.hash import md5_crypt
from ..utils import exceptions_util as exception
from datetime import timedelta

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
    "/get/{user_id}",
    response_model=User_Pydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def get_user(user_id: int):
    """查询单个用户."""
    log.debug(f"{await Users.get(id=user_id).values()}")
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@user_route.put(
    "/update/{user_id}",
    response_model=User_Pydantic,
    responses={404: {"model": HTTPNotFoundError}}
)
async def update_user(user_id: int, user: UserIn_Pydantic):
    """更新用户信息."""
    await Users.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@user_route.delete("/delete/{user_id}",
                   response_model=schemas.Status,
                   responses={404: {"model": HTTPNotFoundError}}
                   )
async def delete_user(user_id: int):
    """删除用户."""
    deleted_count = await Users.filter(id=user_id).delete()
    log.debug("")
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return schemas.Status(message=f"Deleted user {user_id}")


@user_route.post("/login",
                 # response_model=schemas.LoginTo
                 )
async def login(user: schemas.LoginIn):
    """用户登陆."""
    db_user = await Users.filter(username=user.username).first().values()
    if not db_user:
        raise exception.ResponseException(content="user is not exist!")
    if not md5_crypt.verify(secret=user.password, hash=db_user["password"]):
        raise exception.ResponseException(content="Password Error!")
    access_token_expires = timedelta(
        minutes=depends_util.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = depends_util.create_access_token(
        data={"sub": db_user["username"]},
        expires_delta=access_token_expires
    )
    db_user["access_token"] = access_token

    # return schemas.LoginTo(**db_user)
    return db_user
