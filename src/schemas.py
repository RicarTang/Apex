from pydantic import BaseModel, Field, Extra, validator, ValidationError
from .db.models import (
    User_Pydantic,
    Comment_Pydantic,
    Login_pydantic,
    Role_Pydantic,
    Permission_Pydantic,
    DisabledEnum,
    # PermissionIn_Pydantic,
    PermissionCodeEnum,
)
from typing import List, Optional


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
    disabled: Optional[DisabledEnum] = Field(
        default=DisabledEnum.FALSE, description="0:Disable,1:Enable"
    )


class UserIn(User):
    """用户request schema"""

    password: str = Field(min_length=6, max_length=20)


class UserOut(BaseSchema):
    """单用户response schema"""

    data: User_Pydantic

    # class Config:
    #     orm_mode = True


class UsersOut(BaseSchema):
    """用户集response schema"""

    data: List[User_Pydantic]


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


class RoleTo(BaseSchema):
    """角色response schema"""

    data: Role_Pydantic


class PermissionIn(BaseModel):
    """permission request schema"""

    name: str = Field(max_length=20, description="权限名称")
    description: str = Field(max_length=50, description="权限介绍")
    permission_code: PermissionCodeEnum = Field(
        default=PermissionCodeEnum.MEDIUM, description="权限级别码"
    )


class PermissionTo(BaseSchema):
    """permission response schema"""

    data: Permission_Pydantic


class Login(BaseSchema):
    """登录response schema"""

    data: UserPy
    access_token: str
    token_type: str


class LoginIn(BaseModel):
    """登录request schema"""

    username: str
    password: str


# class LoginOut(BaseSchema):


class CommentIn(BaseModel):
    """
    request schema，
    用户单条评论。
    """

    # user_id: int = Field(gt=0, description="用户id")
    comment: str = Field(max_length=50, description="用户评论")


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
