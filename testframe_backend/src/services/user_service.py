from typing import Any
from fastapi import HTTPException, status
from tortoise.queryset import QuerySet
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from ..db.models import Users, Role, UserToken
from ..db.enum import DisabledEnum
from ..utils.log_util import log
from ..utils.exceptions.user import TokenInvalidException, UserNotExistException


class UserService:
    """用户服务."""

    @staticmethod
    async def create_superadmin(**kwargs: Any) -> Users:
        """创建超级管理员

        Returns:
            _type_: _description_
        """
        kwargs["is_super"] = 1
        return await Users.create(**kwargs)

    @staticmethod
    async def query_user_by_username(username: str) -> Users:
        """通过用户名查询用户

        Raises:
            UserNotExistException: _description_

        Returns:
            _type_: _description_
        """
        try:
            query_result = await Users.get(username=username).prefetch_related("roles")
        except DoesNotExist:
            raise UserNotExistException
        except MultipleObjectsReturned:
            log.error("查询出多个同样的用户名！")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Duplicate username!",
            )
        else:
            return query_result

    @staticmethod
    async def create_user(**kwargs):
        """
        创建用户.
        :param kwargs: 用户输入的body
        :return: ORM Model
        """
        return await Users.create(**kwargs)

    @staticmethod
    async def query_user_role(**kwargs) -> QuerySet:
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

    @staticmethod
    async def is_super_user(user_id: int) -> bool:
        """判断是否是超级管理员

        Args:
            user_id (int): 用户id

        Returns:
            bool: _description_
        """
        user = (
            await Users.filter(id=user_id, roles__name="superadmin")
            .first()
            .prefetch_related("roles")
        )
        if user:
            return True
        return False


class UserTokenService:
    """用户token 服务"""

    @staticmethod
    async def add_jwt(current_user_id: int, token: str, client_ip: str) -> None:
        """添加/更新UserToken表数据

        Args:
            current_user_id (int): 当前用户id
            token (str): jwt
            client_ip (str): 客户端ip

        Returns:
            None
        """
        # 查询用户id与客户端ip并且is_active=1的记录，有记录update token，没有记录添加
        if await UserToken.filter(
            user_id=current_user_id, client_ip=client_ip, is_active=DisabledEnum.ENABLE
        ).update(token=token):
            log.debug(f"更新用户{current_user_id}token信息")
        else:
            await UserToken.create(
                token=token, user_id=current_user_id, client_ip=client_ip
            )
            log.debug(f"创建用户{current_user_id}token信息")

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
            # 数据库未记录
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
