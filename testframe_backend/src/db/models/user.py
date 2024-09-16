from typing import Optional, List
from .base_models import Base, CommonMixin
from ..enum import DisabledEnum, BoolEnum, AccessActionEnum, AccessModelEnum
from sqlalchemy import (
    String,
    Integer,
    SmallInteger,
    UniqueConstraint,
    ForeignKey,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship


class User(Base, CommonMixin):
    """用户表映射模型"""

    __tablename__ = "ap_user"
    __table_args__ = (UniqueConstraint("user_name", "is_unique"),)

    user_name: Mapped[str] = mapped_column(String(20), index=True, comment="用户名称")
    password: Mapped[str] = mapped_column(String(128), comment="密码")
    status: Mapped[int] = mapped_column(
        SmallInteger,
        default=DisabledEnum.ENABLE.value,
        index=True,
        comment="用户状态,0:禁用,1:启用",
    )
    remark: Mapped[Optional[str]] = mapped_column(String(50), comment="备注")
    # 关联关系
    roles: Mapped[List["Role"]] = relationship(
        secondary="ap_user_role", back_populates="users"
    )

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


class Role(Base, CommonMixin):
    """角色表映射模型"""

    __tablename__ = "ap_role"
    __table_args__ = (
        UniqueConstraint("role_name", "is_unique"),
        UniqueConstraint("role_key", "is_unique"),
    )

    role_name: Mapped[str] = mapped_column(String(20), comment="角色名称")
    role_key: Mapped[str] = mapped_column(String(20), comment="角色字符")
    remark: Mapped[Optional[str]] = mapped_column(String(50), comment="角色详情")
    is_super: Mapped[int] = mapped_column(
        SmallInteger,
        default=BoolEnum.FALSE.value,
        comment="是否超级管理员角色,1: True,0: False",
    )

    users: Mapped[List[User]] = relationship(
        secondary="ap_user_role", back_populates="roles"
    )

    # permissions: fields.ManyToManyRelation["Permission"] = fields.ManyToManyField(
    #     model_name="models.Permission", related_name="permissions"
    # )
    # menus = fields.ManyToManyField(
    #     model_name="models.Routes", related_name="menus", through="role_menu"
    # )


class UserRole(Base):
    """用户角色关联模型"""

    __tablename__ = "ap_user_role"
    user_id: Mapped[int] = mapped_column(ForeignKey("ap_user.id"), primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("ap_role.id"), primary_key=True)


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
