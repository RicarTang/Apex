from typing import List, Optional
from pydantic import BaseModel, Field, Extra
from ..db.models import User_Pydantic, Role_Pydantic


class User(BaseModel):
    """用户"""

    username: str = Field(max_length=20, description="用户名")
    descriptions: Optional[str] = Field(max_length=50, description="用户描述")
    # is_active: Optional[DisabledEnum] = Field(
    #     default=DisabledEnum.ENABLE, description="0:Disable,1:Enable"
    # )


class UserIn(User):
    """用户req schema"""

    password: str = Field(min_length=6, max_length=20, description="用户密码")
    # user_role: str


class UserOut(User_Pydantic):
    """单用户res schema"""

    pass
    # class Config:
    #     orm_mode = True


class UsersOut(BaseModel):
    """用户集res schema"""

    # List[User_Pydantic]
    data: List[User_Pydantic]
    page: int
    limit: int
    total: int


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


class RolesTo(BaseModel):
    """返回多角色res schema"""

    data: List[Role_Pydantic]
    page: int
    limit: int
    total: int


class UserAddRoleIn(BaseModel):
    """用户添加角色req schema"""

    user_id: int
    role: str


# class UserAddRoleTo(BaseModel):
#     """用户添加角色res schema"""

#     pass


class RolePermIn(BaseModel):
    role: str = Field(..., description="角色")
    model: str = Field(..., description="模块")
    act: str = Field(..., description="权限行为")

    class Config:
        schema_extra = {"example": {"role": "admin", "model": "admin", "act": "add"}}


class Login(BaseModel):
    """登录res schema"""

    data: UserPy
    access_token: str
    token_type: str


class LoginIn(BaseModel):
    """登录req schema"""

    username: str = Field(min_length=2, max_length=20)
    password: str = Field(min_length=6, max_length=20)

    class Config:
        """docs scheam添加example"""

        schema_extra = {"example": {"username": "admin", "password": "123456"}}
