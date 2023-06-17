from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import IntEnum


class TimeStampMixin:
    """创建/更新时间"""

    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    modified_at = fields.DatetimeField(auto_now=True, description="更新时间")


class Disabled(IntEnum):
    TRUE = 1
    FALSE = 0


class Users(models.Model, TimeStampMixin):
    """用户模型"""

    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, unique=True, description="用户名")
    name = fields.CharField(max_length=50, null=True, description="名")
    surname = fields.CharField(max_length=50, null=True, description="姓")
    descriptions = fields.CharField(max_length=30, null=True, description="个人描述")
    password = fields.CharField(max_length=128, description="密码")
    disabled = fields.IntEnumField(
        enum_type=Disabled, default=Disabled.FALSE, description="用户活动状态"
    )
    # 关联关系
    comments: fields.ReverseRelation["Comments"]
    roles: fields.ManyToManyRelation["Role"]

    def __str__(self):
        return str(self.id)

    # def full_name(self) -> str:
    #     """返回全名"""
    #     if self.name or self.surname:
    #         return f"{self.surname or ''} {self.name or ''}".strip()
    #     return self.username

    # class PydanticMeta:
    #     computed = ["full_name"]


class Role(models.Model, TimeStampMixin):
    """角色表"""

    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=20, description="角色名称")
    # 与用户多对多关系
    users: fields.ManyToManyRelation[Users] = fields.ManyToManyField(
        "models.Users", related_name="roles"
    )


class Comments(models.Model, TimeStampMixin):
    """用户评论模型"""

    id = fields.IntField(pk=True, index=True)
    comment = fields.TextField(description="用户评论")
    # 外键
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        model_name="models.Users", related_name="comments"
    )

    def __str__(self):
        return str(self.id)


User_Pydantic = pydantic_model_creator(Users, name="User", exclude=("password",))
Login_pydantic = pydantic_model_creator(Users, name="Login_models")
UserIn_Pydantic = pydantic_model_creator(
    Users, name="UserIn_models", exclude_readonly=True
)
Comment_Pydantic = pydantic_model_creator(Comments, name="CommentTo")
