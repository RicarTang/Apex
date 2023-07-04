from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator
from enum import IntEnum


class TimeStampMixin:
    """创建/更新时间"""

    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_at = fields.DatetimeField(auto_now=True, description="更新时间")


class DisabledEnum(IntEnum):
    """用户disabled枚举"""

    ENABLE = 1
    DISABLE = 0


class PermissionCodeEnum(IntEnum):
    """权限code"""

    LOW = 0
    MEDIUM = 1
    HIGH = 2


class Users(models.Model, TimeStampMixin):
    """用户模型"""

    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, unique=True, description="用户名")
    name = fields.CharField(max_length=50, null=True, description="名")
    surname = fields.CharField(max_length=50, null=True, description="姓")
    descriptions = fields.CharField(max_length=30, null=True, description="个人描述")
    password = fields.CharField(max_length=128, description="密码")
    is_active = fields.IntEnumField(
        enum_type=DisabledEnum,
        default=DisabledEnum.ENABLE,
        description="用户活动状态,0:disable,1:enabled",
    )
    # 关联关系
    comments: fields.ReverseRelation["Comments"]
    roles: fields.ManyToManyRelation["Role"]

    def __str__(self):
        return str(self.username)


class Role(models.Model, TimeStampMixin):
    """角色表"""

    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=20, unique=True, description="角色名称")
    description = fields.CharField(max_length=50, null=True, description="角色详情")

    # 与用户多对多关系
    users: fields.ManyToManyRelation[Users] = fields.ManyToManyField(
        "models.Users", related_name="roles"
    )
    # 与权限表多对多
    # permissions: fields.ManyToManyRelation["Permission"]




class Permission(models.Model, TimeStampMixin):
    """权限表"""

    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=20, unique=True, description="权限名称")
    description = fields.CharField(max_length=50, null=True, description="权限解释")
    permission_code = fields.IntEnumField(
        enum_type=PermissionCodeEnum,
        default=PermissionCodeEnum.MEDIUM,
        description="权限级别代码",
    )
    roles: fields.ManyToManyRelation[Role] = fields.ManyToManyField(
        "models.Role", related_name="permissions"
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


# 用户schema
User_Pydantic = pydantic_model_creator(Users, name="User", exclude=("password",))
Login_pydantic = pydantic_model_creator(Users, name="Login_models")
UserIn_Pydantic = pydantic_model_creator(
    Users, name="UserIn_models", exclude_readonly=True
)
# 评论schema
Comment_Pydantic = pydantic_model_creator(Comments, name="CommentTo")
# 角色schema
Role_Pydantic = pydantic_model_creator(Role, name="RoleTo")
# 权限
PermissionIn_Pydantic = pydantic_model_creator(
    Permission, name="PermissionIo", exclude=("id",), exclude_readonly=True
)
Permission_Pydantic = pydantic_model_creator(Permission, name="PermissionTo")
