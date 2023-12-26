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

    roles: List[RolePydantic] = Field(description="用户角色")


class UsersOut(PageParam):
    """用户集res schema"""

    # List[UserPydantic]
    data: List[UserOut]


class Login(BaseModel):
    """登录res schema"""

    data: UserOut = Field(description="用户信息主体")
    access_token: str = Field(description="jwt")
    token_type: str = Field(description="token类型")


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
