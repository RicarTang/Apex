from pydantic import BaseModel, Field, Extra
from .models import User_Pydantic, Comment_Pydantic, Login_pydantic
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


class Login(BaseSchema, extra=Extra.ignore):
    """
    extra=Extra.ignore,表示忽略多的属性，
    不加时，多了模型没有的属性会报错
    """
    data: Login_pydantic
    # data: User_Pydantic
    access_token: str
    token_type: str


class LoginIn(BaseModel):
    username: str
    password: str


# class LoginOut(BaseSchema):
    


class CommentIn(BaseModel):
    """
    request schema，
    用户单条评论。
    """
    user_id: int = Field(gt=0, description="用户id")
    comment: str = Field(max_length=500, description="用户评论")


class CommentTo(BaseSchema):
    """
    response schema，
    用户单条评论。
    """
    data: Comment_Pydantic


class CommentsTo(BaseSchema):
    """
    response schema，
    某个用户的所有评论。
    """
    data: List[Comment_Pydantic]
