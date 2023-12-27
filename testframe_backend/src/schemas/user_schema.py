from typing import List, Optional
from pydantic import BaseModel, Field, Extra
from ..db.models import UserPydantic, RolePydantic, DisabledEnum
from .common_schema import PageParam


class User(BaseModel):
    """用户"""

    username: str = Field(max_length=20, description="用户名", alias="userName")
    descriptions: Optional[str] = Field(
        default=None, max_length=50, description="用户描述", alias="remark"
    )
    is_active: DisabledEnum = Field(description="0:Disable,1:Enable", alias="status")


class UserIn(User):
    """用户req schema"""

    password: str = Field(min_length=6, max_length=20, description="用户密码")
    user_roles: list = Field(description="角色id列表", alias="roleIds")


class UserUpdateIn(BaseModel):
    """用户更新schema"""

    user_roles: Optional[list] = Field(
        default=None, description="角色id列表", alias="roleIds"
    )
    is_active: Optional[DisabledEnum] = Field(
        default=None, description="0:Disable,1:Enable", alias="status"
    )
    descriptions: Optional[str] = Field(
        default=None, max_length=50, description="用户描述", alias="remark"
    )


class UserTo(UserPydantic):
    """单用户res schema"""

    roles: List[RolePydantic] = Field(description="用户角色")


class UsersTo(PageParam):
    """用户集res schema"""

    # List[UserPydantic]
    data: List[UserTo]


class Login(BaseModel):
    """登录res schema"""

    data: UserTo = Field(description="用户信息主体")
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
