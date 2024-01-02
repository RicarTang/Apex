from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic.alias_generators import to_camel
from ..db.models import (
    PermissionPydantic,
    AccessActionEnum,
    AccessModelEnum,
    RolePydantic,
    RoutesPydantic,
    RouteMetaPydantic,
)
from ..utils.log_util import log
from ..db.enum import BoolEnum
from .common import PageParam


class PermissionIn(BaseModel):
    name: str = Field(description="权限名称", alias="permissionName")


class PermissionAccessIn(BaseModel):
    permission_id: int = Field(description="权限id", alias="permissionId")
    access_id: int = Field(description="访问控制id", alias="accessId")


class RolePermissionIn(BaseModel):
    permission_id: int = Field(description="权限id", alias="permissionId")
    role_id: int = Field(description="角色id", alias="roleId")


class PermissionTo(PermissionPydantic):
    """权限schema"""


class PermissionsTo(PageParam):
    data: List[PermissionTo]


class AccessIn(BaseModel):
    name: str = Field(description="访问控制summary", alias="accessName")
    model: AccessModelEnum = Field(description="权限能访问的模块")
    action: AccessActionEnum = Field(description="权限能操作的动作")


class RoleIn(BaseModel):
    """角色req schema"""

    role_name: str = Field(max_length=20, description="角色名称", alias="roleName")
    role_key: str = Field(max_length=20, description="角色字符", alias="roleKey")
    menu_ids: Optional[List[int]] = Field(
        default=None, description="菜单权限id列表", alias="menuIds"
    )
    permission_ids: Optional[List[int]] = Field(
        default=None, description="权限控制id列表", alias="permissionIds"
    )
    remark: Optional[str] = Field(default=None, max_length=50, description="角色详情")


class RoleTo(RolePydantic):
    """角色res schema"""

    permission_ids: Optional[List[int]] = Field(
        default=None,
        description="角色的权限",
        validation_alias="permissions",
        alias="permissionIds",
    )
    menu_ids: Optional[List[int]] = Field(
        default=None, description="角色的菜单", alias="menuIds", validation_alias="menus"
    )

    @field_validator("menu_ids", mode="before")
    @classmethod
    def modify_menus_before_validation(cls, v):
        """返回menu id"""
        return [menu.id for menu in v]

    @field_validator("permission_ids", mode="before")
    @classmethod
    def modify_permission_before_validation(cls, v):
        """返回permission id"""
        return [permission.id for permission in v]


class RolesTo(PageParam):
    """返回多角色res schema"""

    data: List[RoleTo]


class UserAddRoleIn(BaseModel):
    """用户添加角色req schema"""

    user_id: int = Field(description="用户id", alias="userId")
    role_id: int = Field(description="角色id", alias="roleId")


# class UserAddRoleTo(BaseModel):
#     """用户添加角色res schema"""

#     pass


class RolePermIn(BaseModel):
    role: str = Field(..., description="角色")
    model: str = Field(..., description="模块")
    act: str = Field(..., description="权限行为")
    # docs scheam添加example
    model_config = {
        "json_schema_extra": {
            "example": {"role": "admin", "model": "admin", "act": "add"}
        }
    }
