from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from ..base_models import AbstractBaseModel
from ..enum import DisabledEnum, BoolEnum, AccessActionEnum, AccessModelEnum


class Users(AbstractBaseModel):
    """用户模型"""

    username = fields.CharField(max_length=20, unique=True, description="用户名")
    descriptions = fields.CharField(max_length=30, null=True, description="个人描述")
    password = fields.CharField(max_length=128, index=True, description="密码")
    is_active = fields.IntEnumField(
        enum_type=DisabledEnum,
        default=DisabledEnum.ENABLE,
        description="用户活动状态,0:disable,1:enabled",
    )
    # 关联关系
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        model_name="models.Role", related_name="roles"
    )
    tokens: fields.ReverseRelation["UserToken"]

    class Meta:
        ordering = ["-created_at"]
        indexes = ("username", "is_active", "created_at")  # 添加复合非唯一索引

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


class Role(AbstractBaseModel):
    """角色表"""

    name = fields.CharField(max_length=20, unique=True, description="角色名称")
    description = fields.CharField(max_length=50, null=True, description="角色详情")
    is_super = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.FALSE,
        description="是否超级管理员角色,1: True,0: False",
    )
    permissions: fields.ManyToManyRelation["Permission"] = fields.ManyToManyField(
        model_name="models.Permission", related_name="permissions"
    )

    class Meta:
        ordering = ["-created_at"]


class Permission(AbstractBaseModel):
    """权限表模型"""

    name = fields.CharField(max_length=50, description="权限名称", unique=True)
    accesses: fields.ManyToManyRelation["AccessControl"] = fields.ManyToManyField(
        model_name="models.AccessControl", related_name="accesses"
    )
    menus = fields.ManyToManyField(model_name="models.Routes", related_name="menus")

    class Meta:
        ordering = ["-created_at"]


class AccessControl(AbstractBaseModel):
    """api权限访问控制关联表模型"""

    name = fields.CharField(max_length=50, description="access summary", unique=True)
    model = fields.CharEnumField(
        max_length=30, enum_type=AccessModelEnum, description="模块"
    )
    action = fields.CharEnumField(
        max_length=30,
        enum_type=AccessActionEnum,
        default=AccessActionEnum.GET,
        description="访问控制动作",
    )

    class Meta:
        # 复合唯一索引
        unique_together = ("model", "action")


class UserToken(AbstractBaseModel):
    """用户token模型"""

    token = fields.CharField(max_length=255, index=True, description="用户token令牌")
    is_active = fields.IntEnumField(
        enum_type=DisabledEnum,
        default=DisabledEnum.ENABLE,
        description="令牌状态,0:disable,1:enabled",
    )
    client_ip = fields.CharField(max_length=45, index=True, description="登录客户端IP")
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        model_name="models.Users", related_name="tokens"
    )

    class Meta:
        table = "user_token"


# 用户schema
UserPydantic = pydantic_model_creator(
    Users,
    name="UserTo",
    exclude=("password", "is_delete"),
)

# 角色schema
RolePydantic = pydantic_model_creator(
    Role,
    name="RoleTo",
    exclude=("is_delete",),
)
PermissionPydantic = pydantic_model_creator(
    Permission,
    name="PermissionTo",
    exclude=("is_delete",),
)
AccessPydantic = pydantic_model_creator(
    AccessControl, name="AccessTo", exclude=("is_delete",)
)
