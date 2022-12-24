from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Users(models.Model):
    """用户模型"""

    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20)
    name = fields.CharField(max_length=50, null=True)
    surname = fields.CharField(max_length=50, null=True)
    descriptions = fields.CharField(max_length=30, default="misc")
    password = fields.CharField(max_length=128, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    def full_name(self) -> str:
        """返回全名"""
        if self.name or self.surname:
            return f"{self.surname or ''} {self.name or ''}".strip()
        return self.username

    class PydanticMeta:
        computed = ["full_name"]


User_Pydantic = pydantic_model_creator(Users, name="User", exclude=("password",))
UserIn_Pydantic = pydantic_model_creator(Users, name="UserIn", exclude_readonly=True)
