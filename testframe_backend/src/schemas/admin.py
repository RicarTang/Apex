from typing import List, Optional
from pydantic import BaseModel, Field
from ..db.models import (
    PermissionPydantic,
    AccessActionEnum,
    AccessModelEnum,
    AccessPydantic,
    RolePydantic,
    RoutesPydantic,
    RouteMetaPydantic,
)
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
    accesses: List["AccessTo"] = Field(description="权限访问控制")


class PermissionsTo(PageParam):
    data: List[PermissionTo]


class AccessIn(BaseModel):
    name: str = Field(description="访问控制summary", alias="accessName")
    model: AccessModelEnum = Field(description="权限能访问的模块")
    action: AccessActionEnum = Field(description="权限能操作的动作")


class AccessTo(AccessPydantic):
    pass


class RoleIn(BaseModel):
    """角色req schema"""

    name: str = Field(max_length=20, description="角色名称")
    description: Optional[str] = Field(max_length=50, description="角色详情")


class RoleTo(RolePydantic):
    """角色res schema"""

    permissions: List[PermissionTo] = Field(description="角色的权限")


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


class MenuMeta(BaseModel):
    title: str = Field(description="路由标题")
    icon: str = Field(description="icon图标")
    no_cache: BoolEnum = Field(description="不使用keepalive")
    link: Optional[str] = Field(default=None, description="链接")


class AddMenuIn(BaseModel):
    """添加路由菜单schema"""

    name: str = Field(description="菜单名称")
    path: str = Field(description="菜单path")
    hidden: BoolEnum = Field(description="是否隐藏")
    redirect: Optional[str] = Field(default=None, description="重定向")
    component: str = Field(description="组件path")
    always_show: Optional[BoolEnum] = Field(default=None, description="是否总是显示")
    parent_id: Optional[int] = Field(default=None, description="父菜单id")
    meta: MenuMeta


class AddMenuTo(RoutesPydantic):
    meta: RouteMetaPydantic
    children: Optional[RoutesPydantic] = Field(default=None)
