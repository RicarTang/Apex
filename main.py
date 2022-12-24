# pylint: disable=E0611,E0401
from typing import List

from fastapi import FastAPI, HTTPException
from models import User_Pydantic, UserIn_Pydantic, Users
from pydantic import BaseModel
from tortoise.contrib.fastapi import HTTPNotFoundError, register_tortoise

app = FastAPI(title="Tortoise ORM FastAPI example")
register_tortoise(
    app,
    # db_url="mysql://root:123456@127.0.0.1:3306/tortoise",
    # modules={"models": ["models"]},
    config={
        'connections': {
            'default': "mysql://root:123456@127.0.0.1:3306/tortoise"
        },
        'apps': {
            'models': {
                "models": ["models"],
                'default_connection': 'default',
            }
        },
        "use_tz": False,
        # 设置时区为上海
        "timezone": "Asia/Shanghai",
    },
    generate_schemas=True,
    add_exception_handlers=True,
)


class Status(BaseModel):
    message: str


@app.get("/users", response_model=List[User_Pydantic])
async def get_users():
    return await User_Pydantic.from_queryset(Users.all())


@app.post("/users", response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic):
    user_obj = await Users.create(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_tortoise_orm(user_obj)


@app.get(
    "/user/{user_id}", response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def get_user(user_id: int):
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@app.put(
    "/user/{user_id}", response_model=User_Pydantic, responses={404: {"model": HTTPNotFoundError}}
)
async def update_user(user_id: int, user: UserIn_Pydantic):
    await Users.filter(id=user_id).update(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_queryset_single(Users.get(id=user_id))


@app.delete("/user/{user_id}", response_model=Status, responses={404: {"model": HTTPNotFoundError}})
async def delete_user(user_id: int):
    deleted_count = await Users.filter(id=user_id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return Status(message=f"Deleted user {user_id}")
