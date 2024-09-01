from .base_models import Base
from ..enum import DisabledEnum, BoolEnum, AccessActionEnum, AccessModelEnum
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column


class User(Base):
    """用户表映射模型"""

    __tablename__ = "ap_user"

    user_name: Mapped[str] = mapped_column(String(20), unique=True, comment="用户名称")
    password: Mapped[str] = mapped_column(String(128), comment="密码")
    status: Mapped[int] = mapped_column(
        default=DisabledEnum.ENABLE.value, comment="用户状态,0:禁用,1:启用"
    )
    remark: Mapped[str] = mapped_column(String(50), comment="用户名称")

    # 关联关系
    # roles: fields.ManyToManyRelation["Role"] = fields.ManyToManyField(
    #     model_name="models.Role", related_name="roles", through="user_role"
    # )

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


# class Role(Base):
#     """角色表"""

#     role_name = fields.CharField(max_length=20, unique=True, description="角色名称")
#     role_key = fields.CharField(max_length=20, unique=True, description="角色字符")
#     remark = fields.CharField(max_length=50, null=True, description="角色详情")
#     is_super = fields.IntEnumField(
#         enum_type=BoolEnum,
#         default=BoolEnum.FALSE,
#         description="是否超级管理员角色,1: True,0: False",
#     )
#     permissions: fields.ManyToManyRelation["Permission"] = fields.ManyToManyField(
#         model_name="models.Permission", related_name="permissions"
#     )
#     menus = fields.ManyToManyField(
#         model_name="models.Routes", related_name="menus", through="role_menu"
#     )

#     class Meta:
#         ordering = ["-created_at"]


# class Permission(Base):
#     """权限表模型"""

#     name = fields.CharField(max_length=50, description="access summary", unique=True)
#     model = fields.CharEnumField(
#         max_length=30, enum_type=AccessModelEnum, description="模块"
#     )
#     action = fields.CharEnumField(
#         max_length=30,
#         enum_type=AccessActionEnum,
#         default=AccessActionEnum.GET,
#         description="访问控制动作",
#     )

#     class Meta:
#         ordering = ["-created_at"]
#         # 复合唯一索引
#         unique_together = ("model", "action")
