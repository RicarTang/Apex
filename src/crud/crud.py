"""暂时丢弃此模块。"""
from typing import Union
from tortoise.exceptions import DoesNotExist
from ..db.models import Users, Role, Comments, UserToken
from ..db.enum import DisabledEnum
from ..utils.log_util import log
from ..utils.exception_util import TokenInvalidException


class UsersDao:
    """用户crud."""

    @staticmethod
    async def create_superadmin(**kwargs):
        """创建超级管理员

        Returns:
            _type_: _description_
        """
        kwargs["is_super"] = 1
        return await Users.create(**kwargs)

    @staticmethod
    async def query_user(**kwargs):
        """
        查询用户.
        :param kwargs:
            models字段,
            example：
                id = 1;
                username = "jack"
        :return: QuerySetSingle Type
        """
        return await Users.get(**kwargs)

    @staticmethod
    async def create_user(**kwargs):
        """
        创建用户.
        :param kwargs: 用户输入的body
        :return: ORM Model
        """
        return await Users.create(**kwargs)

    @staticmethod
    async def query_user_role(**kwargs):
        """查询用户角色
        :param kwargs: filter条件
        :return:
        """
        user = await Users.filter(**kwargs).first().prefetch_related("roles")
        user_role_list = await user.roles.all()
        return user_role_list

    @staticmethod
    async def query_user_role_total(**kwargs):
        """查询用户角色total

        Returns:
            _type_: _description_
        """
        user = await Users.filter(**kwargs).first().prefetch_related("roles")


class RolePermDao:
    """角色权限crud"""

    @staticmethod
    async def query_role(**kwargs):
        """查询角色"""
        try:
            role = await Role.get(**kwargs)
        except DoesNotExist:
            return None
        return role

    @staticmethod
    async def add_role_permission(**kwargs):
        """新增角色权限(casbin_rule)"""
        # 查询role是否存在
        # 保存casbin policy
        pass


class UserTokenDao:
    """用户token crud"""

    @staticmethod
    async def add_jwt(
        current_user_id: int, token: str, client_ip: str
    ) -> Union[UserToken, int]:
        """添加/更新UserToken表数据

        Args:
            current_user_id (int): 当前用户id
            token (str): jwt
            client_ip (str): 客户端ip

        Returns:
            Union[UserToken, int]: 更新返回int,创建返回UserToken对象
        """
        # 查询用户id与客户端ip的记录，有记录update token，没有记录添加
        if is_one_ip := await UserToken.filter(
            user_id=current_user_id, client_ip=client_ip
        ).update(token=token):
            return is_one_ip
        else:
            result = await UserToken.create(
                token=token, user_id=current_user_id, client_ip=client_ip
            )
            return result

    @staticmethod
    async def query_jwt_state(token: str) -> bool:
        """查询token状态

        Args:
            token (str): jwt

        Raises:
            TokenInvalidException: token无效

        Returns:
            bool: _description_
        """
        # 数据库查询状态
        if result := await UserToken.filter(token=token).first():
            return result.is_active
        else:
            raise TokenInvalidException

    @staticmethod
    async def update_token_state(token: str) -> int:
        """更新token状态is_active

        Args:
            token (str): _description_

        Returns:
            int: _description_
        """
        result = await UserToken.filter(token=token).update(
            is_active=DisabledEnum.DISABLE
        )
        return result
