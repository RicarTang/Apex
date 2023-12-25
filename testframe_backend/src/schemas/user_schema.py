from typing import List, Optional
from pydantic import BaseModel, Field, Extra
from ..db.models import UserPydantic, RolePydantic, DisabledEnum
from .common_schema import PageParam


class User(BaseModel):
    """用户"""

    username: Optional[str] = Field(default=None, max_length=20, description="用户名")
    descriptions: Optional[str] = Field(default=None, max_length=50, description="用户描述")
    is_active: Optional[DisabledEnum] = Field(
        default=None, description="0:Disable,1:Enable"
    )


class UserIn(User):
    """用户req schema"""

    password: Optional[str] = Field(
        default=None, min_length=6, max_length=20, description="用户密码"
    )
    # user_role: str


class UserOut(UserPydantic):
    """单用户res schema"""

    pass
    # class Config:
    #     orm_mode = True


class UsersOut(PageParam):
    """用户集res schema"""

    # List[UserPydantic]
    data: List[UserPydantic]


class UserPy(UserPydantic, extra=Extra.ignore):
    """
    extra=Extra.ignore,表示忽略多的属性，
    不加时，多了模型没有的属性会报错，
    这里忽略password属性
    """

    pass


class Login(BaseModel):
    """登录res schema"""

    data: UserPy
    access_token: str
    token_type: str


class LoginIn(BaseModel):
    """登录req schema"""

    username: str = Field(min_length=2, max_length=20)
    password: str = Field(min_length=6, max_length=20)
    # docs scheam添加example
    model_config = {
        "json_schema_extra": {"example": {"username": "admin", "password": "123456"}}
    }


class BatchDelete(BaseModel):
    """批量删除用户 req schema"""

    users_id: List[int]
