from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import IntEnum
from .base_models import TimeStampMixin, AbstractBaseModel


class DisabledEnum(IntEnum):
    """用户disabled枚举"""

    ENABLE = 1
    DISABLE = 0

class IsSuperEnum(IntEnum):
    """true / false"""
    TRUE = 1
    FALSE = 0

class Users(AbstractBaseModel, TimeStampMixin):
    """用户模型"""

    username = fields.CharField(max_length=20, unique=True, description="用户名")
    descriptions = fields.CharField(max_length=30, null=True, description="个人描述")
    password = fields.CharField(max_length=128, description="密码")
    is_active = fields.IntEnumField(
        enum_type=DisabledEnum,
        default=DisabledEnum.ENABLE,
        description="用户活动状态,0:disable,1:enabled",
    )
    is_super = fields.IntEnumField(
        enum_type=IsSuperEnum,
        default=IsSuperEnum.FALSE,
        description="用户时候是超级管理员,1: True,0: False"
    )
    # 关联关系
    comments: fields.ReverseRelation["Comments"]
    roles: fields.ManyToManyRelation["Role"]

    def __str__(self):
        return str(self.username)


class Role(AbstractBaseModel, TimeStampMixin):
    """角色表"""

    name = fields.CharField(max_length=20, unique=True, description="角色名称")
    description = fields.CharField(max_length=50, null=True, description="角色详情")

    # 与用户多对多关系
    users: fields.ManyToManyRelation[Users] = fields.ManyToManyField(
        "models.Users", related_name="roles"
    )


class Comments(AbstractBaseModel, TimeStampMixin):
    """用户评论模型"""

    comment = fields.TextField(description="用户评论")
    # 外键
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        model_name="models.Users", related_name="comments"
    )

    def __str__(self):
        return str(self.id)


# 用户schema
User_Pydantic = pydantic_model_creator(
    Users, name="User", exclude=("password", "is_delete")
)
Login_pydantic = pydantic_model_creator(Users, name="Login_models")
UserIn_Pydantic = pydantic_model_creator(
    Users, name="UserIn_models", exclude_readonly=True
)
# 评论schema
Comment_Pydantic = pydantic_model_creator(Comments, name="CommentTo")
# 角色schema
Role_Pydantic = pydantic_model_creator(Role, name="RoleTo", exclude_readonly=True)
