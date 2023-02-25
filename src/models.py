from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class TimeStampMixin:
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    modified_at = fields.DatetimeField(auto_now=True, description="更新时间")


class Users(models.Model, TimeStampMixin):
    """用户模型"""

    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, unique=True, description="用户名")
    name = fields.CharField(max_length=50, null=True, description="名")
    surname = fields.CharField(max_length=50, null=True, description="姓")
    descriptions = fields.CharField(max_length=30, null=True, description="个人描述")
    password = fields.CharField(max_length=128, description="密码")
    # 类型提示
    comments: fields.ReverseRelation["Comments"]

    def full_name(self) -> str:
        """返回全名"""
        if self.name or self.surname:
            return f"{self.surname or ''} {self.name or ''}".strip()
        return self.username

    class PydanticMeta:
        computed = ["full_name"]


class Comments(models.Model, TimeStampMixin):
    id = fields.IntField(pk=True, index=True)
    comment = fields.TextField(null=True, description="用户评论")
    # 外键
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        model_name="models.Users",
        related_name="comments"
    )


User_Pydantic = pydantic_model_creator(Users, name="User", exclude=("password",))
Login_pydantic = pydantic_model_creator(Users, name="Login_models")
UserIn_Pydantic = pydantic_model_creator(Users, name="UserIn_models", exclude_readonly=True)
