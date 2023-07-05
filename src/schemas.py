from typing import List, Optional, TypeVar, Generic
from pydantic import BaseModel, Field, Extra, validator, ValidationError
from pydantic.generics import GenericModel
from .db.models import (
    User_Pydantic,
    Comment_Pydantic,
    # Login_pydantic,
    Role_Pydantic,
    DisabledEnum,
)


DataT = TypeVar("DataT")


class ResultResponse(GenericModel, Generic[DataT]):
    """
    自定义返回模型，使用 generic-models 定义自定义模型
    https://pydantic-docs.helpmanual.io/usage/models/#generic-models
    所有返回数据都用如下格式，方便前端统一处理
    {
        code: 200,
        message: '请求成功',
        data: None
    }
    """

    code: int = Field(default=200, description="返回码")
    message: str = Field(default="请求成功", description="消息内容")
    result: Optional[DataT]


class BaseSchema(BaseModel):
    """success状态"""

    success: bool = Field(default=True)


class Status(BaseSchema):
    message: str


class User(BaseModel):
    """用户"""

    username: str
    surname: Optional[str]
    name: Optional[str]
    descriptions: Optional[str] = Field(max_length=50)
    is_active: Optional[DisabledEnum] = Field(
        default=DisabledEnum.ENABLE, description="0:Disable,1:Enable"
    )


class UserIn(User):
    """用户request schema"""

    password: str = Field(min_length=6, max_length=20)


class UserOut(User_Pydantic):
    """单用户response schema"""

    pass
    # class Config:
    #     orm_mode = True


class UsersOut(List[User_Pydantic]):
    """用户集response schema"""

    # List[User_Pydantic]
    pass


class UserPy(User_Pydantic, extra=Extra.ignore):
    """
    extra=Extra.ignore,表示忽略多的属性，
    不加时，多了模型没有的属性会报错，
    这里忽略password属性
    """

    pass


class RoleIn(BaseModel):
    """角色request schema"""

    name: str = Field(max_length=20, description="角色名称")
    description: Optional[str] = Field(max_length=50, description="角色详情")


class RoleTo(Role_Pydantic):
    """角色response schema"""

    pass


class Login(BaseModel):
    """登录response schema"""

    data: UserPy
    access_token: str
    token_type: str


class LoginIn(BaseModel):
    """登录request schema"""

    username: str
    password: str

    class Config:
        """docs scheam添加example"""
        schema_extra = {"example": {"username": "tang", "password": "123456"}}


# class LoginOut(BaseSchema):


class CommentIn(BaseModel):
    """
    request schema，
    用户单条评论。
    """

    # user_id: int = Field(gt=0, description="用户id")
    comment: str = Field(max_length=50, description="用户评论")


class CommentTo(Comment_Pydantic):
    """
    response schema，
    用户单条评论。
    """

    pass

class CommentsTo(List[Comment_Pydantic]):
    """
    response schema，
    某个用户的所有评论。
    """

    pass