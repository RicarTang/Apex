from typing import List
from pydantic import BaseModel, Field
from ..db.models import (
    PermissionPydantic,
    AccessActionEnum,
    AccessModelEnum,
    AccessPydantic,
)


class PermissionIn(BaseModel):
    name: str = Field(description="权限名称", alias="permissionName")


class PermissionAccessIn(BaseModel):
    permission_id: int = Field(description="权限id",alias="permissionId")
    access_id: int = Field(description="访问控制id",alias="accessId")

class RolePermissionIn(BaseModel):
    permission_id: int = Field(description="权限id",alias="permissionId")
    role_id: int = Field(description="角色id",alias="roleId")

class PermissionTo(PermissionPydantic):
    pass


class AccessIn(BaseModel):
    name: str = Field(description="访问控制summary",alias="accessName")
    model: AccessModelEnum = Field(description="权限能访问的模块")
    action: AccessActionEnum = Field(description="权限能操作的动作")


class AccessTo(AccessPydantic):
    pass
