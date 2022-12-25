from pydantic import BaseModel, Field, Extra
from .models import User_Pydantic
from typing import List, Optional


class BaseSchema(BaseModel):
    success: bool = Field(default=True)


class Status(BaseSchema):
    message: str


class User(BaseModel):
    username: str
    surname: Optional[str]
    name: Optional[str]
    descriptions: Optional[str] = Field(max_length=50)


class UserIn(User):
    password: str = Field(min_length=6, max_length=20)


class UserOut(BaseSchema):
    data: User_Pydantic

    class Config:
        orm_mode = True


class UsersOut(BaseSchema):
    data: List[User_Pydantic]


class Login(User_Pydantic, extra=Extra.ignore):
    """
    extra=Extra.ignore,表示忽略多的属性，
    不加时，多了模型没有的属性会报错
    """
    access_token: str


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseSchema):
    data: Login
