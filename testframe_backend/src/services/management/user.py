from typing import Any, Optional, List, Tuple
from datetime import datetime
from passlib.hash import md5_crypt
from fastapi import HTTPException, status
from sqlalchemy import select, insert, update, and_, func, CursorResult
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, IntegrityError
from ...db import async_session
from ...db.models import User
from ...db.enum import DisabledEnum
from ...schemas.management.user import UserIn
from ...utils.log_util import log
from ...utils.exceptions.user import TokenInvalidException, UserNotExistException
from .admin import RoleService


class UserService:
    """用户服务类"""

    @staticmethod
    async def query_user_list(
        username: Optional[str],
        status: Optional[str],
        begin_time: Optional[str],
        end_time: Optional[str],
        limit: Optional[int],
        page: Optional[int],
    ) -> Tuple[List[dict], int]:
        """查询用户列表

        Args:
        username (Optional[str]): 用户名关键字
        status (Optional[str]): 用户状态
        begin_time (Optional[str]): 开始时间（格式: YYYY-MM-DD）
        end_time (Optional[str]): 结束时间（格式: YYYY-MM-DD）
        limit (Optional[int]): 每页条目数
        page (Optional[int]): 当前页码

        Returns:
            Tuple[List[dict], int]: 用户列表及总记录数
        """
        # 构建查询条件
        filters = []
        if username:
            filters.append(User.user_name.like(f"%{username}%"))
        if status:
            filters.append(User.status == status)
        if begin_time:
            begin_time = datetime.strptime(begin_time, "%Y-%m-%d")
        if end_time:
            end_time = datetime.strptime(end_time, "%Y-%m-%d")
        if begin_time and end_time:
            filters.append(User.created_at.between(begin_time, end_time))
        elif begin_time:
            filters.append(User.created_at >= begin_time)
        elif end_time:
            filters.append(User.created_at <= end_time)
        # 使用事务自动管理并提交
        async with async_session() as session:
            async with session.begin():
                # 创建查询语句，加载关联的 roles 数据，并进行分页
                query = (
                    # select(User).options(selectinload(User.roles)).where(and_(*filters))
                    select(User)
                    .options(selectinload(User.roles))
                    .where(*filters, User.deleted == 0)
                )

                # 执行查询，进行分页
                user_list = await session.scalars(
                    query.offset(limit * (page - 1)).limit(limit)
                )
                # 查询总数
                user_total = await session.scalar(
                    select(func.count(User.id))
                    .where(*filters, User.deleted == 0)
                )
                return user_list.all(), user_total

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
                    result = await session.scalar(
                        select(User)
                        .options(selectinload(User.roles))
                        .where(User.user_name == username, User.deleted == 0)
                    )
                    if not result:
                        raise UserNotExistException
                    return result
        except NoResultFound:
            raise UserNotExistException
        except MultipleResultsFound:
            log.error("查询出多个同样的用户名！")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Duplicate username!",
            )

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

    @staticmethod
    async def query_user_by_id(id: int) -> User:
        """通过id查询用户

        Raises:
            UserNotExistException: _description_

        Returns:
            dict: 查询结果
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    # query_result = await Users.get(id=id).prefetch_related("roles")
                    result = await session.scalar(
                        select(User)
                        .options(selectinload(User.roles))
                        .where(User.id == id, User.deleted == 0)  # 过滤已逻辑删除
                    )
                    if not result:
                        raise UserNotExistException
                    return result
        except NoResultFound:
            raise UserNotExistException
        except MultipleResultsFound:
            log.error("查询出多个同样的用户！")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Duplicate username!",
            )

    @staticmethod
    async def create_user(req_body: UserIn) -> CursorResult:
        """创建用户

        Args:
            req_body (UserIn):  请求体数据

        Returns:
            _type_: _description_
        """
        try:
            async with async_session() as session:
                req_body.password = md5_crypt.hash(req_body.password)
                user = User(
                    **req_body.model_dump(exclude_unset=True, exclude=["user_roles"])
                )
                # result = await session.execute(
                #     insert(User).values(
                #         **req_body.model_dump(
                #             exclude_unset=True, exclude=["user_roles"]
                #         )
                #     )
                # )

                roles = await RoleService.query_role_by_id_list(req_body.user_roles)
                user.roles.extend(roles)
                session.add(user)
                await session.commit()
                log.info(f"成功创建用户：{req_body.model_dump(exclude_unset=True)}")
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="用户已存在!",
            )
        except Exception as e:
            await session.rollback()
            log.error(f"创建用户数据：{req_body.model_dump()}失败,原因:{e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建用户失败!",
            )

    @staticmethod
    async def update_user_pwd(user_id: int, user_new_pwd: str):
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    update(User)
                    .where(User.id == user_id, User.deleted == 0)
                    .values(password=md5_crypt.hash(user_new_pwd))
                )
                # 没有任何更新，表示没有该用户
                if result.rowcount == 0:
                    raise UserNotExistException

    @staticmethod
    async def delete_user(user_ids: str) -> None:
        """逻辑删除用户

        Args:
            user_ids (str): 用户id组成的字符串

        Raises:
            HTTPException: _description_
            UserNotExistException: _description_
        """
        # 解析User ids 为列表
        source_ids_list = user_ids.split(",")
        async with async_session() as session:
            async with session.begin():
                # 检查是否存在admin用户
                # admin_user_ids = await Users.filter(
                #     id__in=source_ids_list, user_name="admin"
                # ).exists()
                # # 禁止删除admin用户
                # if admin_user_ids:
                #     raise HTTPException(
                #         status_code=status.HTTP_403_FORBIDDEN,
                #         detail="admin is prohibited from being deleted",
                #     )
                # delete_count = await Users.filter(
                #     id__in=source_ids_list, user_name__not="admin"
                # ).delete()
                result = await session.execute(
                    # 使用update deleted字段逻辑删除
                    update(User)
                    .where(and_(User.id.in_(source_ids_list), User.deleted == 0))
                    .values(deleted=1, is_unique=None)
                )
                if not result.rowcount:
                    raise UserNotExistException

    @staticmethod
    async def query_user_role_by_id(user_id: int):
        """查询用户角色

        Args:
            user_id (int): _description_

        Returns:
            _type_: _description_
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    user = await session.scalar(
                        select(User)
                        .options(selectinload(User.roles))
                        .where(User.id == user_id, User.deleted == 0)
                    )
                    if not user:
                        raise UserNotExistException
                    return user.roles
        except NoResultFound:
            raise UserNotExistException

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
