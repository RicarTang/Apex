from typing import Any
from passlib.hash import md5_crypt
from fastapi import HTTPException, status
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession
from ...db import async_session
from ...db.models import User
from ...db.enum import DisabledEnum
from ...schemas.management.user import UserIn
from ...utils.log_util import log
from ...utils.exceptions.user import TokenInvalidException, UserNotExistException


class UserService:
    """用户服务."""

    @staticmethod
    async def query_user_list()  :
        async with async_session() as session:
                async with session.begin():
                    sql = select(User)
                    user_list = await session.scalars(sql)
                    return user_list.all()


    @staticmethod
    async def query_user_by_username(username: str) -> User:
        """用户名查询用户

        Raises:
            UserNotExistException: _description_

        Returns:
            _type_: _description_
        """

        try:
            async with async_session() as session:
                async with session.begin():
                    user = select(User).where(user_name=username)
                    return user
        except Exception:
            pass

        # try:
        #     query_result = await Users.get(user_name=username).prefetch_related("roles")
        # except DoesNotExist:
        #     raise UserNotExistException
        # except MultipleObjectsReturned:
        #     log.error("查询出多个同样的用户名！")
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Duplicate username!",
        #     )
        # else:
        #     return query_result

    # @staticmethod
    # async def query_user_by_id(id: int) -> Users:
    #     """通过id查询用户

    #     Raises:
    #         UserNotExistException: _description_

    #     Returns:
    #         _type_: _description_
    #     """
    #     try:
    #         query_result = await Users.get(id=id).prefetch_related("roles")
    #     except DoesNotExist:
    #         raise UserNotExistException
    #     except MultipleObjectsReturned:
    #         log.error("查询出多个同样的用户名！")
    #         raise HTTPException(
    #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #             detail="Duplicate username!",
    #         )
    #     else:
    #         return query_result

    @staticmethod
    async def create_user(req_body: UserIn):
        """
        创建用户.
        :param kwargs: request body
        :return: ORM Model
        """
        try:
            async with async_session() as session:
                async with session.begin():

                    # user_obj = await Users.create(**body.model_dump(exclude_unset=True))
                    # # 查询角色列表
                    # roles = await Role.filter(id__in=body.user_roles).all()
                    # log.debug(roles)
                    # if not roles:
                    #     raise RoleNotExistException
                    # # 添加角色关联
                    # await user_obj.roles.add(*roles)

                    req_body.password = md5_crypt.hash(req_body.password)
                    sql = (
                        insert(User)
                        .values(**req_body.model_dump(exclude_unset=True,exclude=["user_roles"]))
                        .returning(User)
                    )
                    user = await session.execute(sql)
                    log.debug(user)
                    log.info(f"成功创建用户：{req_body.model_dump(exclude_unset=True)}")
                    return user

        except Exception as e:
            log.error(f"创建用户数据：{req_body.model_dump()}失败,原因{e}")

    # @staticmethod
    # async def query_user_role(**kwargs) -> QuerySet:
    #     """查询用户角色
    #     :param kwargs: filter条件
    #     :return:
    #     """
    #     user = await Users.filter(**kwargs).first().prefetch_related("roles")
    #     user_role_list = await user.roles.all()
    #     return user_role_list

    # @staticmethod
    # async def query_user_role_total(**kwargs):
    #     """查询用户角色total

    #     Returns:
    #         _type_: _description_
    #     """
    #     user = await Users.filter(**kwargs).first().prefetch_related("roles")

    # @staticmethod
    # async def is_super_user(user_id: int) -> bool:
    #     """判断是否是超级管理员

    #     Args:
    #         user_id (int): 用户id

    #     Returns:
    #         bool: _description_
    #     """
    #     user = (
    #         await Users.filter(id=user_id, roles__is_super=True)
    #         .first()
    #         .prefetch_related("roles")
    #     )
    #     if user:
    #         return True
    #     return False
