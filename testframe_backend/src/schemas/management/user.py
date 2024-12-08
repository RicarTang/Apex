"""user schemas"""

from typing import List, Optional
from pydantic import BaseModel, Field
from ...db.models import BoolEnum
from ..common import PageParam, CommonMixinModel


class UserMixinModel(BaseModel):
    """用户Mixin"""

    user_name: str = Field(max_length=20, description="用户名", alias="userName")
    remark: Optional[str] = Field(default=None, max_length=50, description="用户描述")
    status: BoolEnum = Field(description="0:Disable,1:Enable")


class UserIn(UserMixinModel):
    """用户req schema"""

    password: str = Field(min_length=6, max_length=20, description="用户密码")
    user_roles: list = Field(description="角色id列表", alias="roleIds")


class UserUpdateIn(BaseModel):
    """用户更新schema"""

    user_roles: Optional[list] = Field(
        default=None, description="角色id列表", alias="roleIds"
    )
    status: Optional[BoolEnum] = Field(default=None, description="0:Disable,1:Enable")
    remark: Optional[str] = Field(
        default=None, max_length=50, description="用户描述", alias="remark"
    )


class UserResetPwdIn(BaseModel):
    """用户重置密码schema"""

    user_id: int = Field(description="用户id", alias="userId")
    password: str = Field(min_length=6, max_length=20, description="用户密码")


class UserOut(CommonMixinModel):
    """用户res schema"""

    user_name: Optional[str] = Field(default=None, serialization_alias="userName")
    # password: Optional[str] = Field(default=None)
    status: Optional[int] = Field(default=None)
    remark: Optional[str] = Field(default=None)
    roles: List["RoleMixinModel"] = Field(description="用户角色")


class RoleMixinModel(CommonMixinModel):
    """角色Mixin"""

    role_name: Optional[str] = Field(default=None, serialization_alias="roleName")
    role_key: Optional[str] = Field(default=None, serialization_alias="roleKey")
    remark: Optional[str] = Field(default=None)
    is_super: Optional[int] = Field(default=None, serialization_alias="isSuper")


class UserListOut(PageParam):
    """用户列表res schema"""

    data: List[UserOut]


# class UserListQuery(CommonListQueryMixinModel):
#     """用户列表查询参数"""

#     username: Optional[str] = Field(
#         default=None,
#         description="用户名",
#         alias="userName",
#     )
#     status: Optional[str] = Field(default=None, description="用户状态")
