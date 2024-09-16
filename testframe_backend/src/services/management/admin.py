from typing import List, NamedTuple, Optional, Tuple
from datetime import datetime
from sqlalchemy import select, insert, update, and_, func, CursorResult
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound, MultipleResultsFound, IntegrityError
from ...db import async_session
from ...db.models import User, Role
from ...utils.log_util import log
from ...utils.exceptions.admin import RoleNotExistException


class RoleService:
    """角色service"""

    @staticmethod
    async def query_role_list(
        role_name: Optional[str],
        role_key: Optional[str],
        begin_time: Optional[str],
        end_time: Optional[str],
        limit: Optional[int],
        page: Optional[int],
    ) -> Tuple[List[dict], int]:
        """查询角色列表

        Args:
            role_name (Optional[str]): _description_
            role_key (Optional[str]): _description_
            begin_time (Optional[str]): _description_
            end_time (Optional[str]): _description_
            limit (Optional[int]): _description_
            page (Optional[int]): _description_

        Raises:
            RoleNotExistException: _description_
            RoleNotExistException: _description_

        Returns:
            Tuple[List[dict], int]: _description_
        """
        # 筛选列表

        filters = []
        if role_name:
            filters.append(Role.role_name.like(f"%{role_name}%"))
        if role_key:
            filters.append(Role.role_name == role_key)
        if begin_time:
            begin_time = datetime.strptime(begin_time, "%Y-%m-%d")
        if end_time:
            end_time = datetime.strptime(end_time, "%Y-%m-%d")
        if begin_time and end_time:
            filters.append(Role.created_at.between(begin_time, end_time))
        elif begin_time:
            filters.append(Role.created_at >= begin_time)
        elif end_time:
            filters.append(Role.created_at <= end_time)
        async with async_session() as session:
            async with session.begin():
                query = select(Role).where(*filters, Role.deleted == 0)
                result = await session.scalars(
                    query.offset(limit * (page - 1)).limit(limit)
                )
                # 查询总数
                total = await session.scalar(
                    select(func.count(Role.id)).where(*filters, Role.deleted == 0)
                )
                # query = Role.filter(**filters)
                # result = (
                #     await query.prefetch_related(
                #         "permissions", "menus__children__route_meta", "menus__route_meta"
                #     )
                #     .offset(limit * (page - 1))
                #     .limit(limit)
                #     .all()
                # )
                return result.all(), total

    @staticmethod
    async def query_role_by_id(role_id: int):
        """role id查询角色

        Args:
            role_id (int): _description_

        Returns:
            _type_: _description_
        """
        try:
            async with async_session() as session:
                async with session.begin():
                    role = await session.scalar(
                        select(Role).where(id == role_id, Role.deleted == 0)
                    )
                    if not role:
                        raise RoleNotExistException
                    return role
        except NoResultFound:
            raise RoleNotExistException

    @staticmethod
    async def query_role_by_id_list(role_id_list: List[int]) -> list:
        """通过role id list 查询角色

        Args:
            role_id_list (List[int]): _description_

        Returns:
            list: _description_
        """
        async with async_session() as session:
            async with session.begin():
                result = await session.scalars(
                    select(Role).where(Role.id.in_(role_id_list), Role.deleted == 0)
                )
                if not result:
                    raise RoleNotExistException
                return result.all()
