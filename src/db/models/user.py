from tortoise import fields
from ..base_models import AbstractBaseModel
from ...utils.enum import BoolEnum, BoolEnum, AccessActionEnum, AccessModelEnum


class Users(AbstractBaseModel):
    """用户模型"""

    user_name = fields.CharField(max_length=20, unique=True, description="用户名")
    remark = fields.CharField(max_length=30, null=True, description="个人描述")
    password = fields.CharField(max_length=128, index=True, description="密码")
    status = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.TRUE,
        description="用户活动状态,0:disable,1:enabled",
    )
    # 关联关系
    roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
        model_name="models.Role", related_name="roles", through="user_role"
    )

    class Meta:
        table = "user"
        ordering = ["-created_at"]
        indexes = ("user_name", "status", "created_at")  # 添加复合非唯一索引

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


class Role(AbstractBaseModel):
    """角色表"""

    role_name = fields.CharField(max_length=20, unique=True, description="角色名称")
    role_key = fields.CharField(max_length=20, unique=True, description="角色字符")
    remark = fields.CharField(max_length=50, null=True, description="角色详情")
    is_super = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.FALSE,
        description="是否超级管理员角色,1: True,0: False",
    )
    permissions: fields.ManyToManyRelation["Permission"] = fields.ManyToManyField(
        model_name="models.Permission", related_name="permissions"
    )
    menus = fields.ManyToManyField(
        model_name="models.Routes", related_name="menus", through="role_menu"
    )

    class Meta:
        ordering = ["-created_at"]


class Permission(AbstractBaseModel):
    """权限表模型"""

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
        ordering = ["-created_at"]
        # 复合唯一索引
        unique_together = ("model", "action")
