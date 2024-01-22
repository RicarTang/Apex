from typing import Any
from fastapi import HTTPException, status
from tortoise.queryset import QuerySet
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from ..db.models import Users, Role
from ..db.enum import DisabledEnum
from ..utils.log_util import log
from ..utils.exceptions.user import TokenInvalidException, UserNotExistException


class UserService:
    """用户服务."""

    @staticmethod
    async def query_user_by_username(username: str) -> Users:
        """通过用户名查询用户

        Raises:
            UserNotExistException: _description_

        Returns:
            _type_: _description_
        """
        try:
            query_result = await Users.get(user_name=username).prefetch_related("roles")
            log.debug(query_result)
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
    async def query_user_by_id(id: int) -> Users:
        """通过id查询用户

        Raises:
            UserNotExistException: _description_

        Returns:
            _type_: _description_
        """
        try:
            query_result = await Users.get(id=id).prefetch_related("roles")
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
            await Users.filter(id=user_id, roles__is_super=True)
            .first()
            .prefetch_related("roles")
        )
        if user:
            return True
        return False
