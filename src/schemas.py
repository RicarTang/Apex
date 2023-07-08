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
        message: 'success',
        data: None
    }
    """

    code: int = Field(default=200, description="返回码")
    message: str = Field(default="success", description="消息内容")
    result: Optional[DataT]


class User(BaseModel):
    """用户"""

    username: str
    descriptions: Optional[str] = Field(max_length=50)
    is_active: Optional[DisabledEnum] = Field(
        default=DisabledEnum.ENABLE, description="0:Disable,1:Enable"
    )


class UserIn(User):
    """用户req schema"""

    password: str = Field(min_length=6, max_length=20)
    user_role: str


class UserOut(User_Pydantic):
    """单用户res schema"""

    pass
    # class Config:
    #     orm_mode = True


class UsersOut(List[User_Pydantic]):
    """用户集res schema"""

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
    """角色req schema"""

    name: str = Field(max_length=20, description="角色名称")
    description: Optional[str] = Field(max_length=50, description="角色详情")


class RoleTo(Role_Pydantic):
    """角色res schema"""

    pass


class UserAddRoleIn(BaseModel):
    """用户添加角色req schema"""

    user_id: int
    role: str

class UserAddRoleTo(BaseModel):
    """用户添加角色res schema"""
    pass


class Login(BaseModel):
    """登录res schema"""

    data: UserPy
    access_token: str
    token_type: str


class LoginIn(BaseModel):
    """登录req schema"""

    username: str
    password: str

    class Config:
        """docs scheam添加example"""

        schema_extra = {"example": {"username": "tang", "password": "123456"}}


# class LoginOut(BaseSchema):


class CommentIn(BaseModel):
    """
    req schema，
    用户单条评论。
    """

    # user_id: int = Field(gt=0, description="用户id")
    comment: str = Field(max_length=50, description="用户评论")


class CommentTo(Comment_Pydantic):
    """
    res schema，
    用户单条评论。
    """

    pass


class CommentsTo(List[Comment_Pydantic]):
    """
    res schema，
    某个用户的所有评论。
    """

    pass
