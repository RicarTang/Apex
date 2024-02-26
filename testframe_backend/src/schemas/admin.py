from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from ..db.models import (
    AccessActionEnum,
    AccessModelEnum,
)
from .common import PageParam, DefaultModel


class PermissionIn(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "admin", "model": "user", "action": "add"}
        }
    )
    name: str = Field(description="权限名称", alias="permissionName")
    model: AccessModelEnum = Field(description="权限能访问的模块", alias="permissionModule")
    action: AccessActionEnum = Field(description="权限能操作的动作", alias="permissionAction")


class PermissionTo(DefaultModel):
    """权限 res schema"""

    # model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(default=None, serialization_alias="permissionName")
    model: Optional[str] = Field(default=None, serialization_alias="permissionModule")
    action: Optional[str] = Field(default=None, serialization_alias="permissionAction")


class PermissionsTo(PageParam):
    data: List[PermissionTo]


class PutPermissionIn(BaseModel):
    name: Optional[str] = Field(
        default=None, description="权限名称", alias="permissionName"
    )
    model: Optional[AccessModelEnum] = Field(
        default=None, description="权限能访问的模块", alias="permissionModule"
    )
    action: Optional[AccessActionEnum] = Field(
        default=None, description="权限能操作的动作", alias="permissionAction"
    )


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


class RoleTo(DefaultModel):
    """角色res schema"""

    model_config = ConfigDict(from_attributes=True)

    role_name: Optional[str] = Field(default=None, serialization_alias="roleName")
    role_key: Optional[str] = Field(default=None, serialization_alias="roleKey")
    is_super: Optional[int] = Field(default=None, serialization_alias="isSuper")
    remark: Optional[str] = Field(default=None)
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


